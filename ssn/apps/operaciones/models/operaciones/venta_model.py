from django.core.exceptions import ValidationError
from django.db import models

from ..base_model import BaseOperacionModel
from ..choices import TipoValuacion
from .detalle_operacion_model import DetalleOperacionBase


class VentaOperacion(BaseOperacionModel, DetalleOperacionBase):
    fecha_pase_vt = models.DateField(
        blank=True,
        null=True,
        help_text=(
            "Fecha de pase a Valor Técnico (DDMMYYYY). "
            "Solo para TP y ON contabilizados a valor técnico"
        ),
    )
    precio_pase_vt = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=(
            "Precio de pase a Valor Técnico. "
            "Solo para TP y ON contabilizados a valor técnico"
        ),
    )
    precio_venta = models.DecimalField(
        max_digits=6, decimal_places=2, help_text="Precio de venta"
    )
    solicitud = models.ForeignKey(
        "operaciones.BaseRequestModel",
        on_delete=models.CASCADE,
        related_name="ventas",
        null=True,
        blank=True,
        help_text="Solicitud a la que pertenece esta venta",
    )

    def clean(self):
        super().clean()
        errors = {}

        # Valuación técnica requiere fecha y precio de pase
        if self.tipo_valuacion == TipoValuacion.TECNICO:
            if not self.fecha_pase_vt:
                errors["fecha_pase_vt"] = (
                    "Debe cargar una fecha de pase a VT para valuación técnica."
                )
            if self.precio_pase_vt is None:
                errors["precio_pase_vt"] = (
                    "Debe cargar un precio de pase a VT para valuación técnica."
                )

        # Si se cargó fecha de pase, también debe cargarse el precio
        if self.fecha_pase_vt and self.precio_pase_vt is None:
            errors["precio_pase_vt"] = (
                "Si se indica fecha de pase VT, debe cargar el precio de pase."
            )

        # Validaciones generales
        if self.precio_venta <= 0:
            errors["precio_venta"] = "El precio de venta debe ser mayor a cero."

        if self.cant_especies <= 0:
            errors["cant_especies"] = "La cantidad de especies debe ser mayor a cero."

        if self.fecha_liquidacion < self.fecha_movimiento:
            errors["fecha_liquidacion"] = (
                "La fecha de liquidación no puede ser anterior a la de movimiento."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.codigo_especie} x {self.cant_especies}"

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        db_table = "db_ventas_operacion"
