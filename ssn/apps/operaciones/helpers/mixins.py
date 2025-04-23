import logging

from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from ..models import BaseRequestModel
from .model_utils import get_mapping_model

# Configuración del logger
logger = logging.getLogger("operaciones")


class HeaderButtonMixin:
    """
    Mixin que proporciona métodos para generar botones de navegación en el encabezado.
    Permite estandarizar la creación de botones "volver" y otros controles.
    """

    def get_back_button(self, url_name, extra_kwargs=None, use_uuid=True):
        """
        Genera un botón 'Volver atrás' centralizado para toda la aplicación.

        Args:
            url_name: Nombre de la URL a la que redirigir
            extra_kwargs: Parámetros adicionales para la URL
            use_uuid: Indica si se debe incluir el UUID de la solicitud base

        Returns:
            dict: Definición del botón para la plantilla
        """
        if extra_kwargs is None:
            extra_kwargs = {}

        if use_uuid and hasattr(self, "base_request") and self.base_request:
            uuid_str = str(self.base_request.uuid)
            logger.debug(f"Generando botón 'volver' a {url_name} con UUID {uuid_str}")
            kwargs = {"uuid": uuid_str, **extra_kwargs}
        else:
            logger.debug(f"Generando botón 'volver' a {url_name} sin UUID")
            kwargs = extra_kwargs

        return {
            "href": reverse(url_name, kwargs=kwargs),
            "label": "Volver atrás",
            "icon": "fas fa-chevron-left",
            "color": "secondary",
        }


class BaseRequestMixin:
    """
    Mixin para recuperar y validar la solicitud base a partir del UUID en la URL.
    Gestiona la coherencia entre la sesión y la URL, redirigiendo en caso de discrepancia.
    """

    from ..services import SessionService

    def dispatch(self, request, *args, **kwargs):
        """
        Intercepta la petición para verificar y establecer la solicitud base.

        Args:
            request: Objeto HttpRequest

        Returns:
            HttpResponse: Respuesta de la vista o redirección en caso de error
        """
        url_uuid = kwargs.get("uuid")
        session_uuid = request.session.get("base_request_uuid")

        # Validación: si no hay UUID en la URL, redirige al inicio
        if not url_uuid:
            logger.warning("Intento de acceso a vista protegida sin UUID en la URL")
            messages.error(request, "No se encontró una solicitud activa.")
            return redirect("operaciones:solicitud_base")

        # Validar coherencia entre sesión y URL
        if session_uuid and str(session_uuid) != str(url_uuid):
            logger.warning(
                f"Discrepancia entre UUID de sesión ({session_uuid}) y URL ({url_uuid})"
            )
            messages.warning(
                request,
                "La solicitud actual no coincide con la sesión. Se ha reiniciado el proceso.",
            )
            self.SessionService.clear_base_request(request)
            self.SessionService.clear_operations(request)
            return redirect("operaciones:solicitud_base")

        # Si no había UUID en sesión, lo establecemos
        if not session_uuid:
            logger.debug(f"Estableciendo UUID de sesión: {url_uuid}")
            request.session["base_request_uuid"] = str(url_uuid)
            request.session.modified = True

        # Validación segura del objeto base
        try:
            self.base_request = BaseRequestModel.objects.get(uuid=url_uuid)
            logger.debug(f"Solicitud base recuperada: {url_uuid}")
        except BaseRequestModel.DoesNotExist:
            logger.error(f"UUID solicitado no existe en la base de datos: {url_uuid}")
            messages.error(request, "La solicitud seleccionada no existe.")
            self.SessionService.clear_base_request(request)
            self.SessionService.clear_operations(request)
            return redirect("operaciones:solicitud_base")

        return super().dispatch(request, *args, **kwargs)


class CommonContextMixin:
    """
    Mixin que agrega información común al contexto de la plantilla:
    título, botón, base_request y opciones de encabezado.
    """

    titulo = ""
    boton_texto = ""
    header_buttons = []

    def get_header_buttons(self):
        """
        Devuelve la lista de botones para el encabezado.
        Se puede sobreescribir en las vistas derivadas.

        Returns:
            list: Lista de definiciones de botones
        """
        return self.header_buttons

    def get_common_context(self, context):
        """
        Agrega al contexto existente los elementos comunes a todas las vistas.

        Args:
            context: Contexto base

        Returns:
            dict: Contexto enriquecido
        """
        from ..services import SessionService

        extra_info = ""
        if hasattr(self, "base_request"):
            logger.debug(
                f"Obteniendo información extra para solicitud {self.base_request.uuid}"
            )
            extra_info = SessionService.get_extra_info(self.request)
            context["base_request"] = self.base_request

        context.update(
            {
                "title": self.titulo,
                "boton_texto": self.boton_texto,
                "header_buttons": self.get_header_buttons(),
                "extra_info": extra_info,
            }
        )
        return context

    def get_context_data(self, **kwargs):
        """
        Implementación estándar para obtener el contexto enriquecido.

        Returns:
            dict: Contexto completo para la plantilla
        """
        context = super().get_context_data(**kwargs)
        return self.get_common_context(context)


class PaginationMixin:
    """
    Mixin para facilitar la paginación de queryset y objetos.
    Gestiona las excepciones comunes de la paginación.
    """

    paginate_by = 10

    def paginate_queryset(self, queryset):
        """
        Pagina un queryset y maneja excepciones de paginación.

        Args:
            queryset: QuerySet o lista a paginar

        Returns:
            tuple: (página actual, objeto paginador)
        """
        if not queryset:
            logger.debug("Intento de paginar un queryset vacío")
            return [], Paginator([], self.paginate_by)

        paginator = Paginator(queryset, self.paginate_by)
        page = self.request.GET.get("page")

        try:
            logger.debug(
                f"Paginando queryset de {paginator.count} elementos, página {page}"
            )
            return paginator.page(page), paginator
        except PageNotAnInteger:
            logger.debug(f"Número de página no válido: '{page}', usando página 1")
            return paginator.page(1), paginator
        except EmptyPage:
            logger.debug(f"Página {page} fuera de rango, usando página 1")
            return paginator.page(1), paginator


class OperacionModelViewMixin:
    """
    Recupera el modelo dinámico usando 'tipo_operacion' de la URL.
    Permite que las vistas trabajen con diferentes modelos según el tipo.
    """

    def get_model_class(self):
        """
        Obtiene la clase de modelo correspondiente al tipo de operación.

        Returns:
            Model: Clase de modelo para el tipo de operación

        Raises:
            Http404: Si el tipo de operación no existe
        """
        tipo_operacion = self.kwargs.get("tipo_operacion")
        mapping = get_mapping_model()

        logger.debug(f"Buscando modelo para tipo de operación: {tipo_operacion}")
        model_class = mapping.get(tipo_operacion)

        if not model_class:
            logger.error(f"Tipo de operación inválido: {tipo_operacion}")
            messages.error(self.request, "Tipo de operación inválido.")
            raise Http404("Tipo de operación inválido.")

        return model_class

    def get_queryset(self):
        """
        Devuelve el queryset para el modelo dinámico.

        Returns:
            QuerySet: Todos los objetos del modelo para el tipo de operación
        """
        return self.get_model_class().objects.all()

    def get_object(self, queryset=None):
        """
        Obtiene el objeto específico según el ID de la URL.

        Args:
            queryset: QuerySet opcional

        Returns:
            object: Instancia del modelo

        Raises:
            Http404: Si el objeto no existe
        """
        queryset = queryset or self.get_queryset()
        pk = self.kwargs.get("pk")

        logger.debug(
            f"Recuperando objeto con ID {pk} del tipo {self.kwargs.get('tipo_operacion')}"
        )
        try:
            return get_object_or_404(queryset, pk=pk)
        except Http404:
            logger.warning(
                f"Objeto con ID {pk} no encontrado para tipo {self.kwargs.get('tipo_operacion')}"
            )
            raise


# ============
# Vistas base
# ============


class StandaloneFormMixin(HeaderButtonMixin, CommonContextMixin):
    """
    Mixin base para formularios independientes que no requieren UUID en la URL.
    Ideal para BaseRequestFormView y formularios iniciales.
    """

    def get_context_data(self, **kwargs):
        """
        Implementación específica para formularios independientes.

        Returns:
            dict: Contexto completo para la plantilla
        """
        context = super().get_context_data(**kwargs)
        return self.get_common_context(context)


class OperacionBaseContextView(BaseRequestMixin, HeaderButtonMixin, CommonContextMixin):
    """
    Clase base para vistas que usan base_request y encabezados.
    Combina la funcionalidad de varios mixins para facilitar el desarrollo.
    """

    def get_context_data(self, **kwargs):
        """
        Implementación específica para vistas de operaciones.

        Returns:
            dict: Contexto completo para la plantilla
        """
        context = super().get_context_data(**kwargs)
        return self.get_common_context(context)


class OperacionFormMixin(OperacionBaseContextView, FormView):
    """
    Vista base para formularios de operaciones.
    Proporciona la estructura común para formularios relacionados con operaciones.
    """

    def form_invalid(self, form):
        """
        Manejo personalizado para formularios inválidos.

        Args:
            form: Formulario con errores

        Returns:
            HttpResponse: Respuesta con formulario inválido
        """
        if hasattr(self, "tipo_operacion"):
            logger.warning(
                f"Formulario inválido para operación tipo: {self.tipo_operacion}"
            )
        else:
            logger.warning("Formulario inválido")

        for field, errors in form.errors.items():
            for error in errors:
                logger.debug(f"Error en campo '{field}': {error}")

        return super().form_invalid(form)


class OperacionTemplateMixin(OperacionBaseContextView, TemplateView):
    """
    Vista base para templates de operaciones.
    Proporciona la estructura común para vistas informativas o de solo lectura.
    """

    pass


class StandaloneTemplateMixin(HeaderButtonMixin, CommonContextMixin, TemplateView):
    """
    Vista base para templates independientes que no requieren UUID en la URL.
    Combina la funcionalidad de HeaderButtonMixin y CommonContextMixin con TemplateView.
    Útil para vistas informativas o de listado general.
    """

    pass
