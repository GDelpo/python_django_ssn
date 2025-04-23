import datetime
import logging
from http import HTTPStatus
from typing import Any, Dict, Tuple

from django.apps import apps

from ..serializers import serialize_operations

logger = logging.getLogger("operaciones")


class SolicitudSenderService:
    """Servicio para enviar solicitudes a la SSN."""

    def __init__(self, base_request, operations):
        """
        Inicializa el servicio de envío de solicitudes.

        Args:
            base_request: Solicitud base que contiene la información general
            operations: Lista de operaciones financieras a enviar
        """
        self.base_request = base_request
        self.operations = operations
        # Obtener el cliente SSN desde la configuración de la app
        self.ssn_client = apps.get_app_config("ssn_client").ssn_client

    def enviar(self) -> Tuple[Dict[str, Any], int]:
        """
        Envía la solicitud a la SSN en un proceso de dos pasos:
        1. Enviar las operaciones al endpoint de entrega
        2. Confirmar la entrega

        Returns:
            Tuple[Dict[str, Any], int]: (Datos de respuesta, código de estado HTTP)
        """
        # Validar que hay operaciones para enviar
        if not self.operations:
            logger.warning("Intento de envío sin operaciones")
            return {"error": "No hay operaciones para enviar."}, HTTPStatus.BAD_REQUEST

        # Serializar la solicitud base y las operaciones
        payload = serialize_operations(self.base_request, self.operations)
        tipo_entrega = payload.get("tipoEntrega")

        # Validar que hay tipo de entrega
        if not tipo_entrega:
            logger.error("Falta el tipo de entrega en el payload")
            return {"error": "Falta el tipo de entrega."}, HTTPStatus.BAD_REQUEST

        # Paso 1: Enviar entrega
        logger.info(
            f"Enviando operaciones tipo {tipo_entrega} al endpoint entrega{tipo_entrega}"
        )
        entrega_response, entrega_status = self.ssn_client.post_resource(
            f"entrega{tipo_entrega}", data=payload
        )

        # Si hay errores en el primer paso, retornar la respuesta
        if self._is_error_status(entrega_status):
            logger.error(
                f"Error en entrega{tipo_entrega}: {entrega_response} "
                f"(Status: {entrega_status})"
            )
            return entrega_response, entrega_status

        # Paso 2: Confirmar entrega
        # Preparar datos para confirmación (solo los campos necesarios)
        confirm_payload = self._prepare_confirm_payload(payload)

        logger.info(f"Confirmando entrega tipo {tipo_entrega}")
        confirm_response, confirm_status = self.ssn_client.post_resource(
            f"confirmarEntrega{tipo_entrega}", data=confirm_payload
        )

        # Si hay errores en el segundo paso, retornar la respuesta
        if self._is_error_status(confirm_status):
            logger.error(
                f"Error en confirmarEntrega{tipo_entrega}: {confirm_response} "
                f"(Status: {confirm_status})"
            )
            return confirm_response, confirm_status

        # Actualiza send_at tras un envío exitoso
        self._mark_as_sent()

        # Registrar éxito y retornar la respuesta
        logger.info(
            f"Solicitud enviada exitosamente. Status: {confirm_status}, "
            f"Respuesta: {confirm_response}"
        )
        return confirm_response, confirm_status

    def _is_error_status(self, status_code: int) -> bool:
        """
        Determina si un código de estado HTTP indica error.

        Args:
            status_code: Código de estado HTTP

        Returns:
            bool: True si es un código de error (4xx, 5xx), False en caso contrario
        """
        return status_code >= 400

    def _prepare_confirm_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepara el payload para la confirmación extrayendo solo los campos necesarios.

        Args:
            payload: Payload completo de la solicitud

        Returns:
            Dict[str, Any]: Payload reducido para la confirmación
        """
        # Extraer solo los campos necesarios para la confirmación
        fields = ["codigoCompania", "tipoEntrega", "cronograma"]
        return {key: payload[key] for key in fields if key in payload}

    def _mark_as_sent(self) -> None:
        """
        Marca la solicitud como enviada estableciendo la fecha y hora de envío.
        """
        self.base_request.send_at = datetime.datetime.now()
        self.base_request.save()
        logger.info(f"Solicitud {self.base_request.uuid} marcada como enviada")
