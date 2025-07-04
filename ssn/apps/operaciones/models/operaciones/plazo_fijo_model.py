from django.core.exceptions import ValidationError
from django.db import models

from ...helpers import comprobante_upload_path
from ..choices import TipoOperacion


class PlazoFijoOperacion(models.Model):
    tipo_operacion = models.CharField(
        max_length=1,
        choices=TipoOperacion.choices,
        help_text="Tipo de operación: Plazo Fijo",
    )
    tipo_pf = models.CharField(max_length=50, help_text="Tipo de plazo fijo")
    bic = models.CharField(max_length=50, help_text="Código BIC")
    cdf = models.CharField(max_length=50, help_text="Código CDF")
    fecha_constitucion = models.DateField(help_text="Fecha de constitución (DDMMYYYY)")
    fecha_vencimiento = models.DateField(help_text="Fecha de vencimiento (DDMMYYYY)")
    moneda = models.CharField(max_length=3, help_text="Código de moneda")
    valor_nominal_origen = models.FloatField(help_text="Valor nominal origen")
    valor_nominal_nacional = models.FloatField(help_text="Valor nominal nacional")
    codigo_afectacion = models.CharField(max_length=3, help_text="Código de afectación")
    tipo_tasa = models.CharField(max_length=50, help_text="Tipo de tasa")
    tasa = models.FloatField(help_text="Valor de la tasa")
    titulo_deuda = models.BooleanField(help_text="Indica si es título de deuda")
    codigo_titulo = models.CharField(max_length=50, help_text="Código del título")
    comprobante = models.FileField(
        upload_to=comprobante_upload_path,
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

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"Plazo Fijo - {self.bic} - {self.fecha_constitucion}"

    class Meta:
        verbose_name = "Plazo Fijo"
        verbose_name_plural = "Plazos Fijos"
        db_table = "db_plazos_fijos_operacion"
