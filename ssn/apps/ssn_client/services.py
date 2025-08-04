import logging
from http import HTTPStatus

from django.apps import apps
from django.utils import timezone
from operaciones.models import EstadoSolicitud
from ssn_client.models import SolicitudResponse

logger = logging.getLogger("ssn_client")


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
    Envía (POST + Confirmación) o rectifica (PUT) una solicitud al mismo endpoint.
    """
    try:
        from operaciones.serializers import serialize_operations

        # 1) Decidir el método HTTP basado en el estado
        if base_request.estado == EstadoSolicitud.BORRADOR:
            http_method_name = "post_resource"
        elif base_request.estado == EstadoSolicitud.RECTIFICANDO:
            http_method_name = "put_resource"
        else:
            msg = f"La solicitud {base_request.uuid} no se puede procesar en su estado actual."
            logger.warning(msg)
            return ({"error": msg}, HTTPStatus.BAD_REQUEST, None)

        # 2) Validar y serializar
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

        # 3) Ejecutar la llamada a la API (POST o PUT)
        ssn_client = apps.get_app_config("ssn_client").ssn_client
        http_method = getattr(ssn_client, http_method_name)

        endpoint = f"entrega{tipo_entrega}"

        logger.info(
            f"Ejecutando {http_method_name.upper()} en {endpoint} para solicitud {base_request.uuid}"
        )
        response, status = http_method(endpoint, data=payload)

        obj_response = guardar_respuesta_solicitud(
            base_request, endpoint, payload, response, status
        )
        if status >= 400:
            return response, status, obj_response

        # 4) Paso de Confirmación (SOLO PARA ENVÍOS NUEVOS CON POST)
        if base_request.estado == EstadoSolicitud.BORRADOR:
            fields = ["codigoCompania", "tipoEntrega", "cronograma"]
            confirm_payload = {key: payload[key] for key in fields if key in payload}
            endpoint_confirm = f"confirmarEntrega{tipo_entrega}"

            logger.info(f"Confirmando entrega en {endpoint_confirm}")
            response, status = ssn_client.post_resource(
                endpoint_confirm, data=confirm_payload
            )

            obj_response = guardar_respuesta_solicitud(
                base_request, endpoint_confirm, confirm_payload, response, status
            )
            if status >= 400:
                return response, status, obj_response

        # 5) Finalizar: Actualizar el estado del modelo
        base_request.send_at = timezone.now()
        base_request.estado = EstadoSolicitud.ENVIADA
        base_request.save()
        logger.info(f"Solicitud {base_request.uuid} procesada correctamente")

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
