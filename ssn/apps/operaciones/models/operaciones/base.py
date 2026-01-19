from django.db import models
from ..base import BaseOperacionModel
from ..instrumentos import Especie
from ...helpers import comprobante_upload_path, validate_comprobante_file
from ..choices import TipoValuacion

class OperacionConEspecieBase(BaseOperacionModel):
    """
    Clase abstracta que acumula toda la lógica común para una operación
    que involucra una Especie (Compra, Venta, etc.).
    """
    especie = models.ForeignKey(
        Especie,
        on_delete=models.PROTECT,
        related_name="%(class)s_operaciones", # related_name dinámico
        help_text="El instrumento financiero operado",
    )
    cant_especies = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        help_text="Cantidad de especies (valor nominal)",
    )
    codigo_afectacion = models.CharField(max_length=3, help_text="Código de afectación")
    tipo_valuacion = models.CharField(
        max_length=1,
        choices=TipoValuacion.choices,
        help_text="Tipo de valuación (T -> Técnico | V -> Mercado)",
    )
    comprobante = models.FileField(
        upload_to=comprobante_upload_path,
        validators=[validate_comprobante_file],
        null=True,
        blank=True,
    )
    solicitud = models.ForeignKey(
        "operaciones.BaseRequestModel",
        on_delete=models.CASCADE,
        related_name="%(class)s_operaciones", # related_name dinámico
        help_text="Solicitud a la que pertenece esta operación",
    )

    class Meta:
        abstract = True