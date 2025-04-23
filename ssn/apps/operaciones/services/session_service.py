from ..models import BaseRequestModel


class SessionService:
    """
    Servicio para gestionar el estado de la sesión relacionado con operaciones financieras.

    Esta clase proporciona métodos estáticos para almacenar y recuperar información
    de solicitudes base y operaciones asociadas dentro de la sesión del usuario.

    Attributes:
        SESSION_KEY_OPERATIONS (str): Clave para almacenar operaciones en la sesión.
        SESSION_KEY_BASE_REQUEST (str): Clave para almacenar el UUID de la solicitud base.
    """

    SESSION_KEY_OPERATIONS = "operations"
    SESSION_KEY_BASE_REQUEST = "base_request_uuid"

    @staticmethod
    def set_base_request(request, base_request):
        """
        Almacena el UUID de una solicitud base en la sesión.

        Args:
            request (HttpRequest): Objeto request de Django.
            base_request (BaseRequestModel): Instancia de solicitud base a almacenar.
        """
        request.session[SessionService.SESSION_KEY_BASE_REQUEST] = str(
            base_request.uuid
        )
        request.session.modified = True

    @staticmethod
    def get_base_request_uuid(request):
        """
        Recupera el UUID de la solicitud base almacenada en la sesión.

        Args:
            request (HttpRequest): Objeto request de Django.

        Returns:
            str or None: UUID de la solicitud base, o None si no existe.
        """
        return request.session.get(SessionService.SESSION_KEY_BASE_REQUEST)

    @staticmethod
    def clear_base_request(request):
        """
        Elimina la referencia a la solicitud base de la sesión.

        Args:
            request (HttpRequest): Objeto request de Django.
        """
        request.session.pop(SessionService.SESSION_KEY_BASE_REQUEST, None)

    @staticmethod
    def add_operation(request, tipo, instance_id):
        """
        Añade una operación a la lista de operaciones en la sesión.

        Args:
            request (HttpRequest): Objeto request de Django.
            tipo (str): Tipo de operación (C, V, J, P).
            instance_id (int): ID de la instancia del modelo de operación.
        """
        operations = request.session.get(SessionService.SESSION_KEY_OPERATIONS, [])
        operations.append({"tipo": tipo, "instance_id": instance_id})
        request.session[SessionService.SESSION_KEY_OPERATIONS] = operations
        request.session.modified = True

    @staticmethod
    def clear_operations(request):
        """
        Elimina todas las operaciones almacenadas en la sesión.

        Args:
            request (HttpRequest): Objeto request de Django.
        """
        request.session[SessionService.SESSION_KEY_OPERATIONS] = []
        request.session.modified = True

    @staticmethod
    def get_operations_raw(request):
        """
        Devuelve la lista de operaciones crudas desde la sesión.

        Args:
            request (HttpRequest): Objeto request de Django.

        Returns:
            list: Lista de operaciones en formato crudo (dicts o tuplas).
        """
        return request.session.get(SessionService.SESSION_KEY_OPERATIONS, [])

    @staticmethod
    def get_operations_models(request):
        """
        Devuelve una lista de dicts con instancia de modelo y tipo.
        Si no hay operaciones en la sesión, intenta recuperarlas de la base de datos.
        """
        from ..helpers import get_mapping_model, get_related_names_map

        operations_raw = SessionService.get_operations_raw(request)
        operations = []

        # Procesar operaciones de la sesión
        for op in operations_raw:
            if isinstance(op, dict):
                tipo = op.get("tipo")
                instance_id = op.get("instance_id")
            elif isinstance(op, (list, tuple)) and len(op) == 2:
                tipo, instance_id = op
            else:
                continue  # formato inválido, lo ignoramos

            mapping = get_mapping_model()
            model_class = mapping.get(tipo)
            if model_class and instance_id:
                try:
                    instance = model_class.objects.get(id=instance_id)
                    operations.append({"tipo": tipo, "instance": instance})
                except model_class.DoesNotExist:
                    continue

        # Si no hay operaciones en la sesión, intentar recuperarlas de la BD
        if not operations:
            base_request_uuid = SessionService.get_base_request_uuid(request)
            if base_request_uuid:
                try:
                    base_request = BaseRequestModel.objects.get(uuid=base_request_uuid)

                    # Recuperar operaciones relacionadas usando el mapeo
                    mapping = get_mapping_model()
                    related_names = get_related_names_map()
                    temp_operations = []

                    # Recorrer cada tipo de operación
                    for tipo, model_class in mapping.items():
                        related_name = related_names.get(tipo)

                        if related_name:
                            # Obtener las operaciones relacionadas
                            related_manager = getattr(base_request, related_name)
                            for instance in related_manager.all():
                                temp_operations.append(
                                    {"tipo": tipo, "instance": instance}
                                )

                    # Si encontramos operaciones, actualizar la sesión
                    if temp_operations:
                        operations = temp_operations
                        # Actualizar la sesión para futuras solicitudes
                        session_ops = []
                        for op in operations:
                            session_ops.append(
                                {"tipo": op["tipo"], "instance_id": op["instance"].id}
                            )

                        request.session[SessionService.SESSION_KEY_OPERATIONS] = (
                            session_ops
                        )
                        request.session.modified = True

                except BaseRequestModel.DoesNotExist:
                    # Si no existe la base_request, no hacer nada
                    pass

        return operations

    @staticmethod
    def get_extra_info(request):
        """
        Obtiene información adicional sobre la solicitud base y sus operaciones.

        Esta función es útil para mostrar un resumen del estado actual de la solicitud
        en los templates.

        Args:
            request (HttpRequest): Objeto request de Django.

        Returns:
            list: Lista de tuplas (etiqueta, valor) con información sobre la solicitud.
        """
        base_request_uuid = SessionService.get_base_request_uuid(request)
        if not base_request_uuid:
            return []

        try:
            base_request = BaseRequestModel.objects.get(uuid=base_request_uuid)
        except BaseRequestModel.DoesNotExist:
            # Limpia la sesión para evitar errores persistentes
            SessionService.clear_base_request(request)
            SessionService.clear_operations(request)
            return []

        operations = SessionService.get_operations_models(request)

        return [
            ("Tipo de Entrega", base_request.tipo_entrega or "—"),
            ("Cronograma", base_request.cronograma or "—"),
            ("Operaciones", operations),
        ]
