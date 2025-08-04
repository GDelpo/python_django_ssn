from django.db import models


class EstadoSolicitud(models.TextChoices):
    BORRADOR = "BORRADOR", "Borrador"
    ENVIADA = "ENVIADA", "Enviada"
    RECTIFICANDO = "RECTIFICANDO", "Rectificando"


class TipoEntrega(models.TextChoices):
    SEMANAL = "Semanal", "Semanal"
    MENSUAL = "Mensual", "Mensual"


class TipoOperacion(models.TextChoices):
    COMPRA = "C", "Compra"
    VENTA = "V", "Venta"
    CANJE = "J", "Canje"
    PLAZO_FIJO = "P", "Plazo Fijo"


class TipoValuacion(models.TextChoices):
    TECNICO = "T", "Técnico"
    MERCADO = "V", "Mercado"


class TipoEspecie(models.TextChoices):
    TITULOS_PUBLICOS = "TP", "Títulos Públicos"
    OBLIGACIONES_NEGOCIABLES = "ON", "Obligaciones Negociables"
    FONDOS_COMUNES_DE_INVERSIÓN = "FC", "Fondos Comunes de Inversión"
    FIDEICOMISOS_FINANCIEROS = "FF", "Fideicomisos Financieros"
    ACCIONES = "AC", "Acciones"
    OTRAS_INVERSIONES = "OP", "Otras Inversiones"


class TipoTasa(models.TextChoices):
    FIJA = "F", "Fija"
    VARIABLE = "V", "Variable"
