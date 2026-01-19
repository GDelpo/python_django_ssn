from django.core.exceptions import ValidationError
from django.db import models

from ..instrumentos import PlazoFijoInstrumento

from ...helpers import comprobante_upload_path, validate_comprobante_file
from ..choices import TipoOperacion


class PlazoFijoOperacion(models.Model):
    instrumento = models.ForeignKey(
        PlazoFijoInstrumento,
        on_delete=models.PROTECT,
        related_name="operaciones",
        help_text="El instrumento de Plazo Fijo constituido",
    )
    tipo_operacion = models.CharField(
        max_length=1,
        choices=TipoOperacion.choices,
        help_text="Tipo de operación: Plazo Fijo",
    )
    
    fecha_constitucion = models.DateField(help_text="Fecha de constitución (DDMMYYYY)")
    fecha_vencimiento = models.DateField(help_text="Fecha de vencimiento (DDMMYYYY)")
    valor_nominal_origen = models.DecimalField(
        max_digits=10, decimal_places=0, help_text="Valor nominal origen"
    )
    valor_nominal_nacional = models.DecimalField(
        max_digits=10, decimal_places=0, help_text="Valor nominal nacional"
    )
    codigo_afectacion = models.CharField(max_length=3, help_text="Código de afectación")
    comprobante = models.FileField(
        upload_to=comprobante_upload_path,
        validators=[validate_comprobante_file],
        null=True,
        blank=True,
        help_text="Adjunta el comprobante (PDF, imagen, etc.)",
    )
    solicitud = models.ForeignKey(
        "operaciones.BaseRequestModel",
        on_delete=models.CASCADE,
        related_name="plazos_fijos",
        null=True,
        blank=True,
        help_text="Solicitud a la que pertenece este plazo fijo",
    )

    created_at = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, verbose_name="Fecha de Creación"
    )

    updated_at = models.DateTimeField(
        auto_now=True, null=True, blank=True, verbose_name="Última Modificación"
    )

    def clean(self):
        super().clean()
        errors = {}

        if self.fecha_vencimiento <= self.fecha_constitucion:
            errors["fecha_vencimiento"] = (
                "La fecha de vencimiento debe ser posterior a la fecha de constitución."
            )

        if self.valor_nominal_origen <= 0:
            errors["valor_nominal_origen"] = (
                "El valor nominal de origen debe ser mayor a cero."
            )

        if self.valor_nominal_nacional <= 0:
            errors["valor_nominal_nacional"] = (
                "El valor nominal nacional debe ser mayor a cero."
            )

        if self.tasa < 0:
            errors["tasa"] = "La tasa no puede ser negativa."

        if self.titulo_deuda and not self.codigo_titulo:
            errors["codigo_titulo"] = (
                "Debe ingresar el código del Título de Deuda si corresponde."
            )

        if not self.titulo_deuda and self.codigo_titulo:
            errors["codigo_titulo"] = (
                "No debe ingresar código de Título de Deuda si no corresponde."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.cdf}"

    @property
    def fecha_operacion(self):
        return self.fecha_constitucion

    class Meta:
        verbose_name = "Plazo Fijo"
        verbose_name_plural = "Plazos Fijos"
        db_table = "db_plazos_fijos_operacion"
