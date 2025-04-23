from django.db import models
from django.forms import ValidationError

from ..base_model import BaseOperacionModel
from .detalle_operacion_model import DetalleOperacionBase


class CompraOperacion(BaseOperacionModel, DetalleOperacionBase):
    precio_compra = models.DecimalField(
        max_digits=6, decimal_places=2, help_text="Precio de compra"
    )
    solicitud = models.ForeignKey(
        "BaseRequestModel",
        on_delete=models.CASCADE,
        related_name="compras",
        null=True,
        blank=True,
        help_text="Solicitud a la que pertenece esta compra",
    )

    def clean(self):
        super().clean()
        errors = {}

        if self.precio_compra <= 0:
            errors["precio_compra"] = "El precio de compra debe ser mayor a cero."

        if self.fecha_liquidacion < self.fecha_movimiento:
            errors["fecha_liquidacion"] = (
                "La fecha de liquidación no puede ser anterior a la de movimiento."
            )

        if self.cant_especies <= 0:
            errors["cant_especies"] = "La cantidad de especies debe ser mayor a cero."

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.codigo_especie} x {self.cant_especies}"

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        db_table = "db_compras_operacion"
