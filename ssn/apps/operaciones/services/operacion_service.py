class OperacionesService:
    """
    Service central para lógica de consulta y agrupación de operaciones.
    """

    @staticmethod
    def get_all_operaciones(base_request):
        """
        Devuelve TODAS las operaciones asociadas a una solicitud, como una lista única ordenada.
        """
        compras = base_request.compras.all()
        ventas = base_request.ventas.all()
        canjes = base_request.canjes.all()
        plazos_fijos = base_request.plazos_fijos.all()
        operaciones = list(compras) + list(ventas) + list(canjes) + list(plazos_fijos)
        # Ordenar por fecha de movimiento
        operaciones.sort(key=lambda op: op.fecha_operacion)
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
    def get_extra_info(base_request):
        """
        Devuelve información extra para mostrar en los templates.
        """
        operaciones = OperacionesService.get_all_operaciones(base_request)
        return [
            ("Tipo de Entrega", base_request.tipo_entrega or "—"),
            ("Cronograma", base_request.cronograma or "—"),
            ("Operaciones", operaciones),
        ]
