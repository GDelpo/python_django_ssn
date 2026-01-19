import logging
from http import HTTPStatus
from typing import Tuple, Dict, Any, Optional

from django.apps import apps
from django.utils import timezone
from operaciones.models import EstadoSolicitud
from ssn_client.models import SolicitudResponse

logger = logging.getLogger("ssn_client")


# Mapeo de estados SSN a estados internos
class EstadoSSN:
    """Estados que devuelve la API de la SSN"""
    VACIO = "VACÍO"
    CARGADO = "CARGADO"
    PRESENTADO = "PRESENTADO"
    RECTIFICACION_PENDIENTE = "RECTIFICACIÓN PENDIENTE"
    A_RECTIFICAR = "A RECTIFICAR"


def consultar_estado_ssn(
    base_request,
) -> Tuple[Optional[str], Optional[Dict[str, Any]], int]:
    """
    Consulta el estado de una solicitud en la SSN.

    Args:
        base_request: Instancia de BaseRequestModel

    Returns:
        Tupla (estado_ssn, datos_completos, status_code)
        - estado_ssn: String con el estado ("VACÍO", "CARGADO", "PRESENTADO", etc.)
        - datos_completos: Dict con toda la respuesta de la SSN
        - status_code: Código HTTP de la respuesta
    """
    try:
        ssn_client = apps.get_app_config("ssn_client").ssn_client

        # Construir el endpoint según el tipo de entrega
        from operaciones.models import TipoEntrega
        
        tipo_entrega = base_request.tipo_entrega
        if tipo_entrega == TipoEntrega.SEMANAL:
            endpoint_name = "entregaSemanal"
        elif tipo_entrega == TipoEntrega.MENSUAL:
            endpoint_name = "entregaMensual"
        else:
            logger.error(f"Tipo de entrega inválido: {tipo_entrega}")
            return None, {"error": "Tipo de entrega inválido"}, HTTPStatus.BAD_REQUEST

        # Parámetros de consulta
        params = {
            "codigoCompania": base_request.codigo_compania or "0744",
            "cronograma": base_request.cronograma,
        }

        logger.info(
            f"Consultando estado en SSN para solicitud {base_request.uuid}: {endpoint_name}?{params}"
        )

        # Hacer la consulta GET
        response, status = ssn_client.get_resource(endpoint_name, params=params)

        if status >= 400:
            logger.error(f"Error al consultar estado SSN: {status} - {response}")
            return None, response, status

        # Extraer el estado de la respuesta
        estado = response.get("estado", EstadoSSN.VACIO)
        logger.info(f"Estado SSN para {base_request.uuid}: {estado}")

        return estado, response, status

    except Exception as e:
        logger.error(
            f"Excepción al consultar estado SSN para {base_request.uuid}: {str(e)}"
        )
        return None, {"error": str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR


def guardar_respuesta_solicitud(base_request, endpoint, payload, response, status):
    obj, created = SolicitudResponse.objects.update_or_create(
        solicitud=base_request,
        endpoint=endpoint,
        defaults={
            "payload_enviado": payload,
            "respuesta": response,
            "status_http": status,
            "es_error": status >= 400,
        },
    )
    action = "creado" if created else "actualizado"
    logger.info(
        f"Respuesta {action} para solicitud {base_request.uuid} y endpoint {endpoint} (status={status})"
    )
    return obj


def enviar_y_guardar_solicitud(base_request, operations, allow_empty=False):
    """
    Envía una solicitud a la SSN considerando su estado actual.

    Flujo:
    1. Consulta el estado en la SSN
    2. Decide qué acción tomar según el estado:
       - VACÍO/CARGADO: POST nueva entrega + confirmar
       - A RECTIFICAR: PUT para rectificar
       - PRESENTADO: No se puede modificar (error)
       - RECTIFICACIÓN PENDIENTE: Esperando aprobación (error)
    """
    try:
        from operaciones.serializers import serialize_operations

        # 1) Consultar estado actual en la SSN
        logger.info(f"Consultando estado previo para solicitud {base_request.uuid}")
        estado_ssn, datos_ssn, status_consulta = consultar_estado_ssn(base_request)

        if status_consulta >= 400:
            msg = f"No se pudo consultar el estado en la SSN: {datos_ssn.get('error', 'Error desconocido')}"
            logger.error(msg)
            return {"error": msg}, status_consulta, None

        logger.info(
            f"Estado actual en SSN para {base_request.uuid}: {estado_ssn}"
        )

        # 2) Decidir el método HTTP basado en el estado SSN
        http_method_name = None
        necesita_confirmacion = False

        if estado_ssn in [EstadoSSN.VACIO, EstadoSSN.CARGADO]:
            # Puede enviarse una nueva presentación o sobrescribir la cargada
            http_method_name = "post_resource"
            necesita_confirmacion = True
            logger.info("Acción: POST nueva entrega + confirmación")

        elif estado_ssn == EstadoSSN.A_RECTIFICAR:
            # Fue aprobada la rectificativa, se puede rectificar
            http_method_name = "post_resource"  # Según tu collection, rectificar también usa POST
            necesita_confirmacion = True
            logger.info("Acción: POST rectificación + confirmación")

        elif estado_ssn == EstadoSSN.PRESENTADO:
            msg = f"La solicitud ya está PRESENTADA en la SSN. No se puede modificar sin solicitar rectificación primero."
            logger.warning(msg)
            return {"error": msg, "estado_ssn": estado_ssn}, HTTPStatus.CONFLICT, None

        elif estado_ssn == EstadoSSN.RECTIFICACION_PENDIENTE:
            msg = f"Hay una solicitud de rectificación pendiente de aprobación en la SSN."
            logger.warning(msg)
            return (
                {"error": msg, "estado_ssn": estado_ssn},
                HTTPStatus.CONFLICT,
                None,
            )

        else:
            msg = f"Estado SSN desconocido: {estado_ssn}"
            logger.error(msg)
            return {"error": msg}, HTTPStatus.INTERNAL_SERVER_ERROR, None

        # 3) Validar y serializar
        if not operations and not allow_empty:
            return (
                {"error": "No hay operaciones para enviar."},
                HTTPStatus.BAD_REQUEST,
                None,
            )

        payload = serialize_operations(base_request, operations)
        tipo_entrega = payload.get("tipoEntrega")
        if not tipo_entrega:
            return {"error": "Falta el tipo de entrega."}, HTTPStatus.BAD_REQUEST, None

        # 4) Determinar el endpoint según el tipo de entrega
        if tipo_entrega == "Diaria" or tipo_entrega == "1":
            endpoint = "entregaDiaria"
            endpoint_confirm = "confirmarEntregaDiaria"
        elif tipo_entrega == "Semanal" or tipo_entrega == "2":
            endpoint = "entregaSemanal"
            endpoint_confirm = "confirmarEntregaSemanal"
        elif tipo_entrega == "Mensual" or tipo_entrega == "3":
            endpoint = "entregaMensual"
            endpoint_confirm = "confirmarEntregaMensual"
        else:
            msg = f"Tipo de entrega inválido: {tipo_entrega}"
            logger.error(msg)
            return {"error": msg}, HTTPStatus.BAD_REQUEST, None

        # 5) Ejecutar la llamada a la API
        ssn_client = apps.get_app_config("ssn_client").ssn_client
        http_method = getattr(ssn_client, http_method_name)

        logger.info(
            f"Ejecutando {http_method_name.upper()} en {endpoint} para solicitud {base_request.uuid}"
        )
        response, status = http_method(endpoint, data=payload)

        obj_response = guardar_respuesta_solicitud(
            base_request, endpoint, payload, response, status
        )
        if status >= 400:
            logger.error(f"Error en envío: {status} - {response}")
            return response, status, obj_response

        logger.info(f"Envío exitoso: {status} - {response}")

        # 6) Paso de Confirmación (si es necesario)
        if necesita_confirmacion:
            fields = ["codigoCompania", "tipoEntrega", "cronograma"]
            confirm_payload = {key: payload[key] for key in fields if key in payload}

            logger.info(f"Confirmando entrega en {endpoint_confirm}")
            response, status = ssn_client.post_resource(
                endpoint_confirm, data=confirm_payload
            )

            obj_response = guardar_respuesta_solicitud(
                base_request, endpoint_confirm, confirm_payload, response, status
            )
            if status >= 400:
                logger.error(f"Error en confirmación: {status} - {response}")
                return response, status, obj_response

            logger.info(f"Confirmación exitosa: {status} - {response}")

        # 7) Consultar estado final para sincronizar
        estado_final_ssn, _, _ = consultar_estado_ssn(base_request)

        # 8) Actualizar el estado del modelo según el estado SSN
        base_request.send_at = timezone.now()

        # Mapear estado SSN a estado local
        if estado_final_ssn == EstadoSSN.PRESENTADO:
            base_request.estado = EstadoSolicitud.PRESENTADO
        elif estado_final_ssn == EstadoSSN.CARGADO:
            base_request.estado = EstadoSolicitud.CARGADO
        elif estado_final_ssn == EstadoSSN.A_RECTIFICAR:
            base_request.estado = EstadoSolicitud.A_RECTIFICAR
        elif estado_final_ssn == EstadoSSN.RECTIFICACION_PENDIENTE:
            base_request.estado = EstadoSolicitud.RECTIFICACION_PENDIENTE

        base_request.save()
        logger.info(
            f"Solicitud {base_request.uuid} procesada correctamente. Estado final SSN: {estado_final_ssn}"
        )

        return response, status, obj_response

    except Exception as e:
        logger.error(
            f"Error inesperado procesando solicitud {base_request.uuid}: {str(e)}"
        )
        return (
            {"error": "Error inesperado", "detalle": str(e)},
            HTTPStatus.INTERNAL_SERVER_ERROR,
            None,
        )


def solicitar_rectificacion_ssn(base_request) -> Tuple[Dict[str, Any], int, Any]:
    """
    Solicita una rectificación para una entrega PRESENTADA.

    Esta función debe usarse cuando el estado SSN es PRESENTADO y se necesita
    modificar la información. Enviará una solicitud de rectificación que quedará
    en estado RECTIFICACIÓN PENDIENTE hasta que la SSN la apruebe.

    Args:
        base_request: Instancia de BaseRequestModel

    Returns:
        Tupla (response, status_code, obj_response)
    """
    try:
        # 1) Verificar que el estado SSN permita solicitar rectificación
        estado_ssn, datos_ssn, status_consulta = consultar_estado_ssn(base_request)

        if status_consulta >= 400:
            msg = f"No se pudo consultar el estado: {datos_ssn.get('error', 'Error desconocido')}"
            return {"error": msg}, status_consulta, None

        if estado_ssn != EstadoSSN.PRESENTADO:
            msg = f"Solo se puede solicitar rectificación de entregas PRESENTADAS. Estado actual: {estado_ssn}"
            logger.warning(msg)
            return {"error": msg, "estado_ssn": estado_ssn}, HTTPStatus.CONFLICT, None

        # 2) Determinar endpoint de rectificación
        from operaciones.models import TipoEntrega
        
        tipo_entrega = base_request.tipo_entrega
        if tipo_entrega == TipoEntrega.SEMANAL:
            endpoint = "rectificarEntregaSemanal"
        elif tipo_entrega == TipoEntrega.MENSUAL:
            endpoint = "rectificarEntregaMensual"
        else:
            return (
                {"error": "Tipo de entrega inválido"},
                HTTPStatus.BAD_REQUEST,
                None,
            )

        # 3) Preparar payload mínimo (solo identificadores)
        payload = {
            "codigoCompania": base_request.codigo_compania or "0744",
            "tipoEntrega": base_request.tipo_entrega,  # Ya es el valor correcto ("Semanal" o "Mensual")
            "cronograma": base_request.cronograma,
        }

        # 4) Enviar solicitud de rectificación (PUT)
        ssn_client = apps.get_app_config("ssn_client").ssn_client
        logger.info(
            f"Solicitando rectificación en {endpoint} para {base_request.uuid}"
        )
        response, status = ssn_client.put_resource(endpoint, data=payload)

        # 5) Guardar respuesta
        obj_response = guardar_respuesta_solicitud(
            base_request, endpoint, payload, response, status
        )

        if status >= 400:
            logger.error(f"Error al solicitar rectificación: {status} - {response}")
            return response, status, obj_response

        # 6) Actualizar estado local a RECTIFICACION_PENDIENTE (no RECTIFICANDO)
        base_request.estado = EstadoSolicitud.RECTIFICACION_PENDIENTE
        base_request.save()

        logger.info(
            f"Solicitud de rectificación enviada correctamente para {base_request.uuid}"
        )
        return response, status, obj_response

    except Exception as e:
        logger.error(
            f"Error inesperado al solicitar rectificación para {base_request.uuid}: {str(e)}"
        )
        return (
            {"error": "Error inesperado", "detalle": str(e)},
            HTTPStatus.INTERNAL_SERVER_ERROR,
            None,
        )
