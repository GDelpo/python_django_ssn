from django.core.exceptions import ValidationError
from django.db import models

from ..base import BaseOperacionModel
from .detalle_operacion import DetalleOperacionCanje


class CanjeOperacion(BaseOperacionModel):
    class Meta:
        verbose_name = "Canje"
        verbose_name_plural = "Canjes"
        db_table = "db_canjes_operacion"

    detalle_a = models.OneToOneField(
        DetalleOperacionCanje,
        on_delete=models.CASCADE,
        related_name="canje_operacion_a",
        help_text="Datos de la operación A",
    )
    detalle_b = models.OneToOneField(
        DetalleOperacionCanje,
        on_delete=models.CASCADE,
        related_name="canje_operacion_b",
        help_text="Datos de la operación B",
    )
    solicitud = models.ForeignKey(
        "operaciones.BaseRequestModel",
        on_delete=models.CASCADE,
        related_name="canjes",
        null=True,
        blank=True,
        help_text="Solicitud a la que pertenece este canje",
    )

    def __str__(self):
        return f"Canje - {self.fecha_movimiento}"

    def clean(self):
        super().clean()
        errors = {}

        if not self.detalle_a or not self.detalle_b:
            errors["detalle_a"] = "Ambos detalles deben estar presentes."
            errors["detalle_b"] = "Ambos detalles deben estar presentes."

        if self.detalle_a == self.detalle_b:
            errors["detalle_b"] = "Los detalles A y B deben ser distintos."

        # Validación cruzada opcional (por ejemplo, detalle_b debe tener fecha posterior a detalle_a)
        if (
            self.detalle_a
            and self.detalle_b
            and self.detalle_a.fecha_pase_vt > self.detalle_b.fecha_pase_vt
        ):
            errors["detalle_b"] = (
                "La fecha de pase VT de B no puede ser anterior a la de A."
            )

        if errors:
            raise ValidationError(errors)
