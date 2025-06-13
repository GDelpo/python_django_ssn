from django.db import models

from .base_model import BaseRequestModel


class SolicitudResponse(models.Model):
    """Almacena la respuesta de la SSN para una solicitud enviada."""

    solicitud = models.ForeignKey(
        BaseRequestModel,
        on_delete=models.CASCADE,
        related_name="respuestas",
        help_text="Solicitud asociada a esta respuesta",
    )
    payload_enviado = models.JSONField(
        help_text="Payload enviado al servicio SSN",
    )
    respuesta = models.JSONField(
        help_text="Respuesta recibida del servicio SSN",
    )
    status_http = models.PositiveIntegerField(help_text="Código HTTP de la respuesta")
    es_error = models.BooleanField(
        default=False, help_text="Indica si la respuesta fue un error"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Respuesta de Solicitud"
        verbose_name_plural = "Respuestas de Solicitud"
        db_table = "db_respuestas_solicitud"
        ordering = ["-created_at"]
