import uuid

from django.core.validators import MinLengthValidator
from django.db import models

from .choices import TipoEntrega, TipoOperacion


class BaseRequestModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo_compania = models.CharField(
        max_length=4,
        validators=[MinLengthValidator(4)],
        help_text="Código identificador de la compañía (4 caracteres)",
    )
    tipo_entrega = models.CharField(
        max_length=10,
        choices=TipoEntrega.choices,
        help_text="Tipo de entrega (semanal o mensual)",
    )
    cronograma = models.CharField(
        max_length=7,
        validators=[MinLengthValidator(7)],
        help_text="Periodo del cronograma (YYYY-MM)",
    )
    operaciones = models.JSONField(
        default=list, help_text="Lista con todas las operaciones en formato JSON"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    send_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Tipo de Entrega: {self.tipo_entrega} | Cronograma: {self.cronograma}"

    class Meta:
        verbose_name = "Solicitud Base"
        verbose_name_plural = "Solicitudes Base"
        db_table = "db_solicitudes_base"
        ordering = ["-created_at"]


class BaseOperacionModel(models.Model):
    tipo_operacion = models.CharField(
        max_length=1,
        choices=TipoOperacion.choices,
        help_text="Tipo de operación a realizar",
    )
    fecha_movimiento = models.DateField(help_text="Fecha de movimiento (DDMMYYYY)")
    fecha_liquidacion = models.DateField(help_text="Fecha de liquidación (DDMMYYYY)")

    class Meta:
        abstract = True
