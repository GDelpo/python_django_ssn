import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from ssn_client.services import enviar_y_guardar_solicitud

from .forms import BaseRequestForm, TipoOperacionForm, create_operacion_form
from .helpers import (
    DynamicModelMixin,
    OperationEditViewMixin,
    OperationReadonlyViewMixin,
    StandaloneViewMixin,
    pretty_json,
)
from .models import BaseRequestModel
from .services import OperacionesService, SessionService, SolicitudPreviewService

logger = logging.getLogger("operaciones")


class SolicitudBaseCreateView(
    StandaloneViewMixin,
    SuccessMessageMixin,
    CreateView,
):
    # --- Atributos configurables ---
    model = BaseRequestModel
    form_class = BaseRequestForm
    template_name = "forms/solicitud.html"
    title = "Formulario de Solicitud"
    button_text = "Agregar Operaciones"
    header_buttons_config = []
    breadcrumbs = [
        ("Inicio", "theme:index"),
        ("Nueva Solicitud", None),
    ]
    success_message = "Solicitud base creada exitosamente."

    # --- Métodos ---
    def get_title(self):
        return self.title

    def get_button_text(self):
        return self.button_text

    def get_header_buttons_config(self):
        return self.header_buttons_config

    def get_breadcrumbs(self):
        return self.breadcrumbs

    def get(self, request, *args, **kwargs):
        recover_uuid = request.GET.get("recover_uuid")
        if recover_uuid:
            logger.info(f"Intentando recuperar solicitud con UUID: {recover_uuid}")
            try:
                base_instance = BaseRequestModel.objects.get(uuid=recover_uuid)
                SessionService.set_base_request(request, base_instance)
                logger.info(f"Solicitud {recover_uuid} recuperada.")
                messages.success(request, "Solicitud recuperada exitosamente.")
                return redirect(
                    "operaciones:seleccion_tipo_operacion", uuid=base_instance.uuid
                )
            except BaseRequestModel.DoesNotExist:
                logger.warning(
                    f"Intento de recuperar UUID no existente: {recover_uuid}"
                )
                messages.error(
                    request, "No se encontró una operación con el UUID proporcionado."
                )
        logger.debug("Mostrando formulario de solicitud base")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        SessionService.set_base_request(self.request, self.object)
        return response

    def get_success_url(self):
        return reverse(
            "operaciones:seleccion_tipo_operacion",
            kwargs={"uuid": str(self.object.uuid)},
        )


class SolicitudBaseListView(
    StandaloneViewMixin,
    ListView,
):
    # --- Atributos configurables ---
    model = BaseRequestModel
    template_name = "lists/lista_solicitudes.html"
    context_object_name = "solicitudes"
    paginate_by = 10
    title = "Listado de Solicitudes"
    header_buttons_config = ["new_base"]
    breadcrumbs = [
        ("Inicio", "theme:index"),
        ("Listado de Solicitudes", None),
    ]

    # --- Métodos ---
    def get_title(self):
        return self.title

    def get_header_buttons_config(self):
        return self.header_buttons_config

    def get_breadcrumbs(self):
        return self.breadcrumbs

    def get_queryset(self):
        SessionService.clear_base_request(self.request)
        return BaseRequestModel.objects.all().prefetch_related("respuestas")


class OperacionListView(
    OperationReadonlyViewMixin,
    ListView,
):
    # --- Atributos configurables ---
    template_name = "lists/lista.html"
    context_object_name = "operations"
    paginate_by = 10
    title = "Tabla de Operaciones"
    breadcrumbs = [
        ("Inicio", "theme:index"),
        ("Solicitudes", "operaciones:lista_solicitudes"),
        (lambda self: f"Solicitud {self.base_request.uuid}", None),
    ]

    # --- Métodos ---
    def get_title(self):
        return self.title

    def get_breadcrumbs(self):
        return self.breadcrumbs

    def get_queryset(self):
        return OperacionesService.get_all_operaciones(self.base_request)

    def get_header_buttons_config(self):
        sent = bool(self.base_request.send_at)
        has_ops = bool(self.get_queryset())
        if sent:
            return ["back_solicitudes", "preview"]
        return ["new_operation"] + (["preview"] if has_ops else [])


class TipoOperacionSelectView(
    OperationReadonlyViewMixin,
    FormView,
):
    # --- Atributos configurables ---
    form_class = TipoOperacionForm
    template_name = "forms/seleccion_tipo_operacion.html"
    title = "Selecciona el Tipo de Operación"
    button_text = "Crear Operación"
    header_buttons_config = ["back_base"]
    breadcrumbs = [
        ("Inicio", "theme:index"),
        ("Solicitud Base", "operaciones:solicitud_base"),
        ("Seleccionar Tipo", None),
    ]

    # --- Métodos ---
    def get_title(self):
        return self.title

    def get_button_text(self):
        return self.button_text

    def get_header_buttons_config(self):
        return self.header_buttons_config

    def get_breadcrumbs(self):
        return self.breadcrumbs

    def form_valid(self, form):
        tipo = form.cleaned_data["tipo_operacion"]
        return redirect(
            "operaciones:crear_operacion",
            uuid=str(self.base_request.uuid),
            tipo_operacion=tipo,
        )


class OperacionCreateView(
    OperationEditViewMixin,
    SuccessMessageMixin,
    CreateView,
):
    # --- Atributos configurables ---
    template_name = "forms/operacion.html"
    title = "Formulario de Operación"
    button_text = "Guardar Operación"
    header_buttons_config = ["back_selection"]
    breadcrumbs = [
        (
            lambda self: f"Solicitud {self.base_request.uuid}",
            "operaciones:lista_operaciones",
            lambda self: {"uuid": self.base_request.uuid},
        ),
        (
            "Tipo de Operación",
            "operaciones:seleccion_tipo_operacion",
            lambda self: {"uuid": self.base_request.uuid},
        ),
        ("Nueva Operación", None),
    ]
    success_message = "Operación creada correctamente."

    # --- Métodos ---
    def get_title(self):
        return self.title

    def get_button_text(self):
        return self.button_text

    def get_header_buttons_config(self):
        return self.header_buttons_config

    def get_breadcrumbs(self):
        return self.breadcrumbs

    def dispatch(self, request, *args, **kwargs):
        self.tipo_operacion = kwargs.get("tipo_operacion")
        self.form_class = create_operacion_form(self.tipo_operacion)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.solicitud = self.base_request
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "operaciones:lista_operaciones",
            kwargs={"uuid": str(self.base_request.uuid)},
        )


class OperacionDetailView(
    OperationReadonlyViewMixin,
    DynamicModelMixin,
    DetailView,
):
    # --- Atributos configurables ---
    template_name = "forms/operacion_readonly.html"
    context_object_name = "operation"
    title = "Detalles de Operación"
    header_buttons_config = ["back_operations"]
    breadcrumbs = [
        ("Inicio", "theme:index"),
        ("Solicitudes", "operaciones:lista_solicitudes"),
        (
            lambda self: f"Solicitud {self.base_request.uuid}",
            "operaciones:lista_operaciones",
            lambda self: {"uuid": self.base_request.uuid},
        ),
        ("Ver Detalle", None),
    ]

    # --- Métodos ---
    def get_title(self):
        return self.title

    def get_header_buttons_config(self):
        return self.header_buttons_config

    def get_breadcrumbs(self):
        return self.breadcrumbs


class OperacionUpdateView(
    OperationEditViewMixin,
    DynamicModelMixin,
    SuccessMessageMixin,
    UpdateView,
):
    # --- Atributos configurables ---
    template_name = "forms/operacion.html"
    title = "Editar Operación"
    button_text = "Actualizar Operación"
    header_buttons_config = ["back_operations"]
    breadcrumbs = [
        ("Inicio", "theme:index"),
        ("Solicitudes", "operaciones:lista_solicitudes"),
        (
            lambda self: f"Solicitud {self.base_request.uuid}",
            "operaciones:lista_operaciones",
            lambda self: {"uuid": self.base_request.uuid},
        ),
        ("Editar Operación", None),
    ]
    success_message = "Operación actualizada correctamente."

    # --- Métodos ---
    def get_title(self):
        return self.title

    def get_button_text(self):
        return self.button_text

    def get_header_buttons_config(self):
        return self.header_buttons_config

    def get_breadcrumbs(self):
        return self.breadcrumbs

    def dispatch(self, request, *args, **kwargs):
        self.tipo_operacion = kwargs.get("tipo_operacion")
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return create_operacion_form(self.tipo_operacion)

    def get_success_url(self):
        return reverse(
            "operaciones:lista_operaciones",
            kwargs={"uuid": str(self.base_request.uuid)},
        )


class OperacionDeleteView(
    OperationEditViewMixin,
    DynamicModelMixin,
    DeleteView,
):
    # --- Atributos configurables ---
    template_name = "forms/operacion_confirm_delete.html"
    title = "Eliminar Operación"
    button_text = "Eliminar Operación"
    header_buttons_config = ["back_operations"]
    breadcrumbs = [
        ("Inicio", "theme:index"),
        ("Solicitudes", "operaciones:lista_solicitudes"),
        (
            lambda self: f"Solicitud {self.base_request.uuid}",
            "operaciones:lista_operaciones",
            lambda self: {"uuid": self.base_request.uuid},
        ),
        ("Eliminar Operación", None),
    ]

    # --- Métodos ---
    def get_title(self):
        return self.title

    def get_button_text(self):
        return self.button_text

    def get_header_buttons_config(self):
        return self.header_buttons_config

    def get_breadcrumbs(self):
        return self.breadcrumbs

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Operación eliminada correctamente.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "operaciones:lista_operaciones",
            kwargs={"uuid": str(self.base_request.uuid)},
        )


class OperacionPreviewView(
    OperationReadonlyViewMixin,
    TemplateView,
):
    # --- Atributos configurables ---
    template_name = "lists/preview.html"
    title = "Vista Previa"

    # --- Métodos ---
    def get_title(self):
        return self.title

    def get_header_buttons_config(self):
        return ["back_operations"] + (["send"] if not self.base_request.send_at else [])

    def get(self, request, *args, **kwargs):
        operations = OperacionesService.get_all_operaciones(self.base_request)
        preview = SolicitudPreviewService(self.base_request, operations)
        if not preview.generar_preview():
            messages.error(request, "No hay operaciones para enviar.")
            return redirect(
                "operaciones:lista_operaciones", uuid=str(self.base_request.uuid)
            )
        self.formatted_json = preview.formatted_json
        self.mailto_link = preview.mailto_link
        self.excel_link = preview.generar_excel()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "formatted_json": self.formatted_json,
                "mailto_link": self.mailto_link,
                "excel_link": self.excel_link,
            }
        )
        return context


class OperacionSendView(
    OperationReadonlyViewMixin,
    View,
):
    # --- Atributos configurables ---
    title = ""  # no aplica, no renderiza un card

    # --- Métodos ---
    def get_title(self):
        return self.title

    def get(self, request, *args, **kwargs):
        operations = OperacionesService.get_all_operaciones(self.base_request)
        allow_empty = not operations and self.base_request.tipo_entrega == "Semanal"
        if not operations and not allow_empty:
            messages.error(request, "No hay operaciones para enviar.")
            return redirect(
                "operaciones:lista_operaciones", uuid=str(self.base_request.uuid)
            )
        response_data, status, response_obj = enviar_y_guardar_solicitud(
            self.base_request, operations, allow_empty=allow_empty
        )
        if 200 <= status < 300:
            messages.success(
                request,
                response_data.get("message", "Solicitud enviada correctamente."),
            )
            SessionService.clear_base_request(request)
            return redirect(settings.HOME_URL or reverse("operaciones:solicitud_base"))
        messages.error(
            request, response_data.get("message", "Error al enviar la solicitud.")
        )
        for err in response_data.get("errors", []):
            messages.error(request, err)
        return redirect(
            "operaciones:lista_operaciones", uuid=str(self.base_request.uuid)
        )


class SolicitudRespuestasListView(
    StandaloneViewMixin,
    DetailView,
):
    # --- Atributos configurables ---
    model = BaseRequestModel
    template_name = "lists/respuestas_por_solicitud.html"
    context_object_name = "solicitud"
    title = "Detalle de Respuestas"
    header_buttons_config = ["back_solicitudes"]
    breadcrumbs = [
        ("Inicio", "theme:index"),
        ("Listado de Solicitudes", "operaciones:lista_solicitudes"),
        ("Detalle de Respuestas", None),
    ]

    # --- Métodos ---
    def get_title(self):
        return self.title

    def get_header_buttons_config(self):
        return self.header_buttons_config

    def get_breadcrumbs(self):
        return self.breadcrumbs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["respuestas"] = [
            {
                "obj": resp,
                "formatted_payload": pretty_json(resp.payload_enviado),
                "formatted_response": pretty_json(resp.respuesta),
            }
            for resp in self.object.respuestas.all().order_by("created_at")
        ]
        return context
