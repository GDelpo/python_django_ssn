"""
Modelo único para stocks mensuales (Inversión, Plazo Fijo y Cheque Pago Diferido).
"""

from django.db import models

from .base_model import BaseRequestModel
from .choices import TipoEspecie, TipoValuacion, TipoTasa


class TipoStock(models.TextChoices):
    INVERSION = "I", "Inversión"
    PLAZO_FIJO = "P", "Plazo Fijo"
    CHEQUE_PD = "C", "Cheque Pago Diferido"


class BaseMonthlyStock(models.Model):
    """
    Abstracto con todos los campos comunes a cualquier stock de entrega mensual.
    """

    tipo = models.CharField(
        max_length=1, choices=TipoStock.choices, help_text="Tipo de stock mensual"
    )
    codigo_afectacion = models.CharField(max_length=3, help_text="Código de afectación")
    libre_disponibilidad = models.BooleanField(
        default=True, help_text="Libre disponibilidad (1: Sí, 0: No)"
    )
    en_custodia = models.BooleanField(
        default=True, help_text="Indicador en custodia (1: Sí, 0: No)"
    )
    financiera = models.BooleanField(default=True, help_text="Indicador financiera")
    valor_contable = models.DecimalField(
        max_digits=14, decimal_places=0, help_text="Valor contable"
    )

    class Meta:
        abstract = True


class BaseMonthlyStockPlazoFijoChequePagoDiferido(BaseMonthlyStock):
    """
    Abstracto con campos comunes a los stocks de Plazo Fijo y Cheque Pago Diferido.
    """

    moneda = models.CharField(max_length=3, help_text="Código de moneda")
    tipo_tasa = models.CharField(
        max_length=1,
        choices=TipoTasa.choices,
        help_text="F si es Fija, V si es Variable",
    )
    tasa = models.DecimalField(
        max_digits=5, decimal_places=3, help_text="Tasa aplicada"
    )

    class Meta:
        abstract = True


class InversionStock(BaseMonthlyStock):
    """
    Stock de tipo Inversión.
    """

    tipo_especie = models.CharField(
        max_length=2,
        choices=TipoEspecie.choices,
        help_text="Tipo de especie (TP, ON, FC, etc.)",
    )
    codigo_especie = models.CharField(
        max_length=20, help_text="Código SSN de la especie"
    )
    cantidad_devengado_especies = models.DecimalField(
        max_digits=20, decimal_places=6, help_text="Cantidad devengada de especies"
    )
    cantidad_percibido_especies = models.DecimalField(
        max_digits=20, decimal_places=6, help_text="Cantidad percibida de especies"
    )
    tipo_valuacion = models.CharField(
        max_length=1, choices=TipoValuacion.choices, help_text="Tipo de valuación"
    )
    con_cotizacion = models.BooleanField(
        default=True, help_text="Indicador de cotización (1: Sí, 0: No)"
    )
    emisor_grupo_economico = models.BooleanField(
        default=False, help_text="Emisor pertenece a grupo económico (1: Sí, 0: No)"
    )
    emisor_art_ret = models.BooleanField(
        default=False, help_text="Emisor ART/RET (1: Sí, 0: No)"
    )
    prevision_desvalorizacion = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        blank=True,
        null=True,
        help_text="Previsión desvalorización",
    )
    fecha_pase_vt = models.DateField(
        blank=True, null=True, help_text="Fecha de pase a VT (DDMMYYYY)"
    )
    precio_pase_vt = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Precio de pase a VT",
    )
    valor_financiero = models.DecimalField(
        max_digits=14, decimal_places=0, help_text="Valor financiero"
    )

    solicitud = models.ForeignKey(
        BaseRequestModel,
        on_delete=models.CASCADE,
        related_name="stocks_inversion_mensuales",
        help_text="Solicitud mensual a la que pertenece este stock",
    )

    class Meta:
        verbose_name = "Stock Inversión Mensual"
        verbose_name_plural = "Stocks Inversión Mensuales"
        ordering = ["-solicitud", "codigo_especie"]

    def __str__(self):
        return f"Inversión {self.codigo_especie} @ {self.solicitud.cronograma}"


class PlazoFijoStock(BaseMonthlyStockPlazoFijoChequePagoDiferido):
    """
    Stock de tipo Plazo Fijo.
    """

    tipo_pf = models.CharField(max_length=3, help_text="Código de Tipo de Depósito")
    bic = models.CharField(max_length=12, help_text="Código BIC del banco")
    cdf = models.CharField(max_length=20, help_text="Certificado del Depósito a Plazo")
    fecha_constitucion = models.DateField(help_text="Fecha de constitución (DDMMYYYY)")
    fecha_vencimiento = models.DateField(help_text="Fecha de vencimiento (DDMMYYYY)")
    valor_nominal_origen = models.DecimalField(
        max_digits=10, decimal_places=0, help_text="Valor nominal en moneda origen"
    )
    valor_nominal_origen = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        help_text="Valor nominal en moneda origen",
        blank=True,
        null=True,
    )
    valor_nominal_nacional = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        help_text="Valor nominal en Pesos Argentinos",
    )
    emisor_grupo_economico = models.BooleanField(
        default=False, help_text="Emisor pertenece a grupo económico (1: Sí, 0: No)"
    )
    titulo_deuda = models.BooleanField(
        default=False,
        help_text="Indicador si está relacionado con un título de deuda pública (1: Sí, 0: No).",
    )
    codigo_titulo = models.CharField(
        max_length=3, blank=True, null=True, help_text="Código de título público"
    )
    solicitud = models.ForeignKey(
        BaseRequestModel,
        on_delete=models.CASCADE,
        related_name="stocks_plazofijo_mensuales",
        help_text="Solicitud mensual a la que pertenece este stock",
    )

    class Meta:
        verbose_name = "Stock Plazo Fijo Mensual"
        verbose_name_plural = "Stocks Plazo Fijo Mensuales"
        ordering = ["-solicitud", "bic"]

    def __str__(self):
        return f"Plazo Fijo {self.bic} @ {self.solicitud.cronograma}"


class ChequePagoDiferidoStock(BaseMonthlyStockPlazoFijoChequePagoDiferido):
    """
    Stock de tipo Cheque Pago Diferido.
    """

    codigo_sgr = models.CharField(max_length=3, help_text="Código SGR")
    codigo_cheque = models.CharField(max_length=16, help_text="Código del cheque")
    fecha_emision = models.DateField(help_text="Fecha de emisión (DDMMYYYY)")
    fecha_vencimiento = models.DateField(help_text="Fecha de vencimiento (DDMMYYYY)")
    valor_nominal = models.DecimalField(
        max_digits=10, decimal_places=0, help_text="Valor nominal del cheque"
    )
    valor_adquisicion = models.DecimalField(
        max_digits=10, decimal_places=0, help_text="Valor de adquisición del cheque"
    )
    grupo_economico = models.BooleanField(
        default=False, help_text="Emisor pertenece a grupo económico (1: Sí, 0: No)"
    )
    fecha_adquisicion = models.DateField(help_text="Fecha de adquisición (DDMMYYYY)")
    solicitud = models.ForeignKey(
        BaseRequestModel,
        on_delete=models.CASCADE,
        related_name="stocks_chequespd_mensuales",
        help_text="Solicitud mensual a la que pertenece este stock",
    )

    class Meta:
        verbose_name = "Stock Cheque Pago Diferido Mensual"
        verbose_name_plural = "Stocks Cheque Pago Diferido Mensuales"
        ordering = ["-solicitud", "codigo_cheque"]

    def __str__(self):
        return f"Cheque {self.codigo_cheque} @ {self.solicitud.cronograma}"
