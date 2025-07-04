"""
Modelos que representan el detalle de una operación.
"""

from django.core.exceptions import ValidationError
from django.db import models

from ...helpers import comprobante_upload_path, validate_comprobante_file
from ..choices import TipoEspecie, TipoValuacion


class DetalleOperacionBase(models.Model):
    tipo_especie = models.CharField(
        max_length=2,
        choices=TipoEspecie.choices,
        help_text="Tipo de especie (2 caracteres)",
    )
    codigo_especie = models.CharField(max_length=20, help_text="Código de la especie")
    cant_especies = models.DecimalField(
        max_digits=20,  # 14 enteros + 6 decimales = 20 dígitos en total
        decimal_places=6,
        help_text="Cantidad de especies (valor nominal): 14 enteros + 6 decimales para FCI, 14 enteros para otras inversiones",
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
        help_text="Adjunta el comprobante (PDF, imagen, etc.)",
    )

    def clean(self):
        super().clean()

        # Validar cant_especies según el tipo de especie
        if hasattr(self, "cant_especies") and self.cant_especies is not None:
            # Obtener la parte decimal
            decimal_part = self.cant_especies % 1

            # Para especies que no son FCI, la parte decimal debe ser cero
            if (
                self.tipo_especie != TipoEspecie.FONDOS_COMUNES_DE_INVERSIÓN
                and decimal_part != 0
            ):
                raise ValidationError(
                    {
                        "cant_especies": "Para este tipo de especie, la cantidad debe ser un número entero sin decimales."
                    }
                )

    def save(self, *args, **kwargs):
        # Si no es FCI y tiene decimales, redondeamos a entero
        if hasattr(self, "cant_especies") and self.cant_especies is not None:
            if self.tipo_especie != TipoEspecie.FONDOS_COMUNES_DE_INVERSIÓN:
                self.cant_especies = int(self.cant_especies)

        super().save(*args, **kwargs)

    @classmethod
    def from_db(cls, db, field_names, values):
        # Crear la instancia como normalmente se hace
        instance = super().from_db(db, field_names, values)

        # Formatear el valor al recuperarlo de la BD
        if hasattr(instance, "cant_especies") and instance.cant_especies is not None:
            if instance.tipo_especie != TipoEspecie.FONDOS_COMUNES_DE_INVERSIÓN:
                # Modificar el valor en memoria, sin cambiar la BD
                instance.cant_especies = int(instance.cant_especies)

        return instance

    class Meta:
        abstract = True
        verbose_name = "Detalle base de operación"
        verbose_name_plural = "Detalles base de operación"


class DetalleOperacionCanje(DetalleOperacionBase):
    fecha_pase_vt = models.DateField(help_text="Fecha de pase a venta (DDMMYYYY)")
    precio_pase_vt = models.DecimalField(
        max_digits=6, decimal_places=2, help_text="Precio de pase a venta"
    )
