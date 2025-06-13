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

    def enviar(self, allow_empty: bool = False) -> Tuple[Dict[str, Any], int]:
        """
        Envía la solicitud a la SSN en dos pasos:
         1) entrega{tipoEntrega}
         2) confirmarEntrega{tipoEntrega}

        Si `allow_empty=True`, no falla cuando no hay operaciones y envía
        `"operaciones": []` de todas formas.

        Returns:
            Tuple[Dict, int]: (datos de respuesta, código HTTP)
        """
        # 1) Validar presencia de operaciones (a menos que permitamos vacío)
        if not self.operations and not allow_empty:
            logger.warning("Intento de envío sin operaciones")
            return {"error": "No hay operaciones para enviar."}, HTTPStatus.BAD_REQUEST

        # 2) Serializar (operaciones será [] si está vacío)
        payload = serialize_operations(self.base_request, self.operations)
        tipo_entrega = payload.get("tipoEntrega")
        if not tipo_entrega:
            logger.error("Falta el tipo de entrega en el payload")
            return {"error": "Falta el tipo de entrega."}, HTTPStatus.BAD_REQUEST

        # 3) Paso 1: enviar entrega
        logger.info(f"Enviando operaciones tipo {tipo_entrega} a entrega{tipo_entrega}")
        entrega_response, entrega_status = self.ssn_client.post_resource(
            f"entrega{tipo_entrega}", data=payload
        )
        if self._is_error_status(entrega_status):
            logger.error(f"Error en entrega{tipo_entrega}: {entrega_response}")
            self._save_response(payload, entrega_response, entrega_status, error=True)
            return entrega_response, entrega_status

        # 4) Paso 2: confirmar entrega
        confirm_payload = self._prepare_confirm_payload(payload)
        logger.info(f"Confirmando entrega tipo {tipo_entrega}")
        confirm_response, confirm_status = self.ssn_client.post_resource(
            f"confirmarEntrega{tipo_entrega}", data=confirm_payload
        )
        if self._is_error_status(confirm_status):
            logger.error(f"Error en confirmarEntrega{tipo_entrega}: {confirm_response}")
            self._save_response(payload, confirm_response, confirm_status, error=True)
            return confirm_response, confirm_status

        # 5) Marcar como enviado
        self._mark_as_sent()
        logger.info(f"Solicitud {self.base_request.uuid} enviada correctamente")
        self._save_response(payload, confirm_response, confirm_status, error=False)
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

    def _save_response(
        self,
        payload: Dict[str, Any],
        response: Dict[str, Any],
        status: int,
        error: bool,
    ) -> None:
        """Guarda la respuesta del servicio asociándola a la solicitud."""
        from ..models import SolicitudResponse

        SolicitudResponse.objects.create(
            solicitud=self.base_request,
            payload_enviado=payload,
            respuesta=response,
            status_http=status,
            es_error=error,
        )
        logger.debug(
            f"Respuesta registrada para {self.base_request.uuid} (error={error})"
        )
