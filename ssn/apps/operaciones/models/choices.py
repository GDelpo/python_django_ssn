from django.db import models


class EstadoSolicitud(models.TextChoices):
    # Estados locales de edición
    BORRADOR = "BORRADOR", "Borrador"
    
    # Estados sincronizados con SSN API
    CARGADO = "CARGADO", "Cargado (sin confirmar)"
    PRESENTADO = "PRESENTADO", "Presentado"
    RECTIFICACION_PENDIENTE = "RECTIFICACION_PENDIENTE", "Rectificación Pendiente"
    A_RECTIFICAR = "A_RECTIFICAR", "Aprobado para Rectificar"
    
    # Estado deprecated - mantener por compatibilidad
    ENVIADA = "ENVIADA", "Enviada (deprecated)"
    RECTIFICANDO = "RECTIFICANDO", "Rectificando (deprecated)"


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
