from ..models import TipoEntrega


class OperacionesService:
    """
    Service central para lógica de consulta y agrupación de operaciones.
    """

    @staticmethod
    def get_all_operaciones(base_request):
        """
        Devuelve TODAS las operaciones asociadas a una solicitud, como una lista única ordenada.
        """
        if base_request.tipo_entrega == TipoEntrega.SEMANAL:
            compras = base_request.compras.all()
            ventas = base_request.ventas.all()
            canjes = base_request.canjes.all()
            plazos_fijos = base_request.plazos_fijos.all()
            operaciones = (
                list(compras) + list(ventas) + list(canjes) + list(plazos_fijos)
            )
            # Ordenar por fecha de movimiento
            operaciones.sort(key=lambda op: op.fecha_operacion)
        elif base_request.tipo_entrega == TipoEntrega.MENSUAL:
            inversiones = base_request.stocks_inversion_mensuales.all()
            plazos_fijos = base_request.stocks_plazofijo_mensuales.all()
            cheques_pd = base_request.stocks_chequespd_mensuales.all()
            operaciones = list(inversiones) + list(plazos_fijos) + list(cheques_pd)
        return operaciones

    @staticmethod
    def get_count_by_tipo(base_request):
        """
        Devuelve un dict con el conteo de operaciones por tipo.
        """
        return {
            "compras": base_request.compras.count(),
            "ventas": base_request.ventas.count(),
            "canjes": base_request.canjes.count(),
            "plazos_fijos": base_request.plazos_fijos.count(),
        }

    @staticmethod
    def get_total_operaciones(base_request):
        """
        Devuelve el total sumando los valores del dict de counts.
        """
        counts = OperacionesService.get_count_by_tipo(base_request)
        return sum(counts.values())

    @staticmethod
    def get_extra_info(base_request):
        """
        Devuelve información extra para mostrar en los templates.
        """
        return [
            ("Tipo de Entrega", base_request.tipo_entrega or "—"),
            ("Cronograma", base_request.cronograma or "—"),
            ("Operaciones", OperacionesService.get_total_operaciones(base_request)),
        ]
