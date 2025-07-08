import logging
from http import HTTPStatus

from django.apps import apps
from django.utils import timezone
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
    try:
        from operaciones.serializers import serialize_operations

        # 0) Chequeo: ¿ya fue enviada?
        if base_request.send_at:
            logger.warning(
                f"La solicitud {base_request.uuid} ya fue enviada el {base_request.send_at}."
            )
            return (
                {"error": f"Esta solicitud ya fue enviada el {base_request.send_at.strftime('%d/%m/%Y %H:%M')}. No se puede volver a enviar."},
                HTTPStatus.BAD_REQUEST,
                None,
            )

        # 1) Validar presencia de operaciones (a menos que permitamos vacío)
        if not operations and not allow_empty:
            logger.warning(
                f"Intento de envío sin operaciones (solicitud {base_request.uuid})"
            )
            return (
                {"error": "No hay operaciones para enviar."},
                HTTPStatus.BAD_REQUEST,
                None,
            )

        # 2) Serializar (operaciones será [] si está vacío)
        payload = serialize_operations(base_request, operations)
        logger.debug(
            f"Payload serializado para solicitud {base_request.uuid}: {payload}"
        )
        tipo_entrega = payload.get("tipoEntrega")
        if not tipo_entrega:
            logger.error(
                f"Falta el tipo de entrega en el payload (solicitud {base_request.uuid})"
            )
            return {"error": "Falta el tipo de entrega."}, HTTPStatus.BAD_REQUEST, None

        ssn_client = apps.get_app_config("ssn_client").ssn_client

        # 3) Paso 1: entrega
        endpoint_entrega = f"entrega{tipo_entrega}"
        logger.info(
            f"Enviando operaciones a {endpoint_entrega} (solicitud {base_request.uuid})"
        )
        entrega_response, entrega_status = ssn_client.post_resource(
            endpoint_entrega, data=payload
        )
        obj_entrega = guardar_respuesta_solicitud(
            base_request, endpoint_entrega, payload, entrega_response, entrega_status
        )
        if entrega_status >= 400:
            logger.error(
                f"Error en {endpoint_entrega}: {entrega_response} (solicitud {base_request.uuid})"
            )
            return entrega_response, entrega_status, obj_entrega

        # 4) Paso 2: confirmar entrega
        fields = ["codigoCompania", "tipoEntrega", "cronograma"]
        confirm_payload = {key: payload[key] for key in fields if key in payload}
        endpoint_confirm = f"confirmarEntrega{tipo_entrega}"
        logger.info(
            f"Confirmando entrega en {endpoint_confirm} (solicitud {base_request.uuid})"
        )
        confirm_response, confirm_status = ssn_client.post_resource(
            endpoint_confirm, data=confirm_payload
        )
        obj_confirm = guardar_respuesta_solicitud(
            base_request, endpoint_confirm, payload, confirm_response, confirm_status
        )
        if confirm_status >= 400:
            logger.error(
                f"Error en {endpoint_confirm}: {confirm_response} (solicitud {base_request.uuid})"
            )
            return confirm_response, confirm_status, obj_confirm

        # 5) Marcar como enviado
        base_request.send_at = timezone.now()
        base_request.save()
        logger.info(f"Solicitud {base_request.uuid} enviada correctamente")
        return confirm_response, confirm_status, obj_confirm

    except Exception as e:
        logger.error(
            f"Error inesperado enviando solicitud {base_request.uuid}: {str(e)}"
        )
        return (
            {"error": "Error inesperado en el servidor", "detalle": str(e)},
            HTTPStatus.INTERNAL_SERVER_ERROR,
            None,
        )
