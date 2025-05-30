import logging

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DeleteView, FormView, UpdateView

# Configuración del logger
logger = logging.getLogger("operaciones")


from .forms import BaseRequestForm, TipoOperacionForm, create_operacion_form
from .helpers import (
    BaseRequestMixin,
    OperacionFormMixin,
    OperacionModelViewMixin,
    OperacionTemplateMixin,
    PaginationMixin,
    StandaloneFormMixin,
    StandaloneTemplateMixin,
    get_mapping_model,
)
from .models import BaseRequestModel
from .services import SessionService, SolicitudPreviewService, SolicitudSenderService


# Vista para crear la solicitud base
class BaseRequestFormView(StandaloneFormMixin, FormView):
    """
    Vista para crear o recuperar la solicitud base que contendrá las operaciones.
    Punto de entrada principal del flujo de creación de solicitudes.
    """

    template_name = "formularios/solicitud.html"
    form_class = BaseRequestForm
    titulo = "Formulario de Solicitud"
    boton_texto = "Agregar Operaciones"

    def get(self, request, *args, **kwargs):
        recover_uuid = request.GET.get("recover_uuid")
        if recover_uuid:
            logger.info(f"Intentando recuperar solicitud con UUID: {recover_uuid}")
            try:
                base_instance = BaseRequestModel.objects.get(uuid=recover_uuid)

                # Limpiar y configurar la sesión
                SessionService.clear_operations(request)
                SessionService.set_base_request(request, base_instance)

                # Usar el SessionService para recuperar las operaciones
                operations = SessionService.get_operations_models(request)

                logger.info(
                    f"Solicitud {recover_uuid} recuperada con {len(operations)} operaciones asociadas"
                )
                messages.success(request, "Operación recuperada exitosamente.")

                # Si hay operaciones recuperadas, redirigir a la lista
                if operations:
                    return redirect(
                        "operaciones:lista_operaciones", uuid=base_instance.uuid
                    )

                # Si no hay operaciones, ir a la selección de tipo
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
        logger.debug("Validando formulario de solicitud base")
        SessionService.clear_operations(self.request)
        base_instance = form.save()
        SessionService.set_base_request(self.request, base_instance)

        logger.info(f"Solicitud base creada exitosamente: {base_instance.uuid}")
        messages.success(self.request, "Solicitud base creada exitosamente.")
        return redirect("operaciones:seleccion_tipo_operacion", uuid=base_instance.uuid)


# Vista para la selección del tipo de operación
class TipoOperacionFormView(OperacionFormMixin):
    """
    Vista para la selección del tipo de operación a crear.
    Segundo paso en el flujo de creación de solicitudes.
    """

    template_name = "formularios/seleccion_tipo_operacion.html"
    form_class = TipoOperacionForm
    titulo = "Selecciona el Tipo de Operación"
    boton_texto = "Continuar"

    def form_valid(self, form):
        # Obtener el valor de la opción seleccionada
        self.tipo_operacion = form.cleaned_data["tipo_operacion"]

        logger.debug(f"Tipo de operación seleccionado: {self.tipo_operacion}")

        # Obtener el mapeo de modelos
        mapping = get_mapping_model()

        # Obtener la clase de modelo correspondiente al tipo de operación
        ModelClass = mapping.get(self.tipo_operacion)

        if ModelClass is None:
            logger.error(
                f"Tipo de operación '{self.tipo_operacion}' no encontrado en el mapeo"
            )
            messages.error(
                self.request,
                f"Tipo de operación '{self.tipo_operacion}' no encontrado.",
            )
            return super().form_valid(form)

        # Crear una instancia temporal del modelo
        instance = ModelClass()
        instance.tipo_operacion = self.tipo_operacion

        # Obtener la etiqueta legible
        tipo_operacion_display = instance.get_tipo_operacion_display()

        logger.info(
            f"Usuario seleccionó operación: '{tipo_operacion_display}' para solicitud {self.base_request.uuid}"
        )
        messages.info(
            self.request, f"Tipo de operación '{tipo_operacion_display}' seleccionado."
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "operaciones:crear_operacion",
            kwargs={
                "uuid": str(self.base_request.uuid),
                "tipo_operacion": self.tipo_operacion,
            },
        )

    def get_header_buttons(self):
        return [self.get_back_button("operaciones:solicitud_base", use_uuid=False)]


# Vista para crear una nueva operación
class OperacionCreateView(OperacionFormMixin):
    """
    Vista para crear una nueva operación del tipo seleccionado.
    Tercer paso en el flujo de creación de solicitudes.
    """

    template_name = "formularios/operacion.html"
    titulo = "Formulario de Operación"
    boton_texto = "Guardar Operación"

    def dispatch(self, request, *args, **kwargs):
        self.tipo_operacion = kwargs.get("tipo_operacion")
        if not self.tipo_operacion:
            logger.warning(
                f"Intento de crear operación sin especificar tipo para solicitud {kwargs.get('uuid')}"
            )
            messages.error(request, "Tipo de operación no especificado.")
            return redirect(
                "operaciones:seleccion_tipo_operacion", uuid=self.kwargs.get("uuid")
            )

        logger.debug(
            f"Generando formulario para tipo de operación: {self.tipo_operacion}"
        )
        self.form_class = create_operacion_form(self.tipo_operacion)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        solicitud_uuid = SessionService.get_base_request_uuid(self.request)

        if solicitud_uuid:
            try:
                solicitud = BaseRequestModel.objects.get(uuid=solicitud_uuid)
                form.instance.solicitud = solicitud
                logger.debug(f"Asociando operación a solicitud: {solicitud_uuid}")
            except BaseRequestModel.DoesNotExist:
                logger.error(f"No se encontró solicitud con UUID: {solicitud_uuid}")
                messages.error(self.request, "No se encontró la solicitud activa.")
                return self.form_invalid(form)
        else:
            logger.error("Intento de crear operación sin solicitud activa en sesión")
            messages.error(self.request, "No hay una solicitud activa en sesión.")
            return self.form_invalid(form)

        operacion_instance = form.save()
        logger.info(
            f"Operación creada: {self.tipo_operacion} (ID: {operacion_instance.id}) para solicitud {solicitud_uuid}"
        )
        SessionService.add_operation(
            self.request, self.tipo_operacion, operacion_instance.id
        )
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Operación creada correctamente")
        return reverse(
            "operaciones:seleccion_tipo_operacion",
            kwargs={"uuid": str(self.base_request.uuid)},
        )

    def get_header_buttons(self):
        return [self.get_back_button("operaciones:seleccion_tipo_operacion")]


# Vista para listar operaciones
class OperationTableView(PaginationMixin, OperacionTemplateMixin):
    """
    Vista para listar todas las operaciones asociadas a una solicitud.
    Muestra la tabla con paginación y opciones de acción.
    """

    template_name = "listados/lista.html"
    titulo = "Tabla de Operaciones"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        logger.debug(f"Obteniendo operaciones para solicitud: {self.base_request.uuid}")
        operations_list = SessionService.get_operations_models(self.request)
        operations_page, paginator = self.paginate_queryset(operations_list)

        # Determinar si la solicitud está enviada (read-only)
        is_readonly = self.base_request.send_at is not None

        context["operations"] = operations_page
        context["paginator"] = paginator
        context["is_readonly"] = is_readonly  # Agregar al contexto

        # Modificar los botones según el estado
        header_buttons = []

        if not is_readonly:
            # Solicitud editable - mostrar botones normales
            header_buttons.extend(
                [
                    {
                        "href": reverse(
                            "operaciones:seleccion_tipo_operacion",
                            kwargs={"uuid": str(self.base_request.uuid)},
                        ),
                        "label": "Nueva Operación",
                        "icon": "fas fa-plus",
                        "color": "primary",
                    },
                    {
                        "href": reverse(
                            "operaciones:preview_operaciones",
                            kwargs={"uuid": str(self.base_request.uuid)},
                        ),
                        "label": "Revisar Solicitud",
                        "icon": "fas fa-eye",
                        "color": "warning",
                        "condition": lambda request: bool(
                            SessionService.get_operations_models(request)
                        ),
                    },
                ]
            )
        else:
            # Solicitud de solo lectura - mostrar botones relevantes para modo lectura
            header_buttons.extend(
                [
                    {
                        "href": reverse("operaciones:lista_solicitudes"),
                        "label": "Volver a la lista",
                        "icon": "fas fa-arrow-left",
                        "color": "secondary",
                    },
                    {
                        "href": reverse(
                            "operaciones:preview_operaciones",
                            kwargs={"uuid": str(self.base_request.uuid)},
                        ),
                        "label": "Revisar Solicitud",
                        "icon": "fas fa-eye",
                        "color": "warning",
                    },
                ]
            )

        context["header_buttons"] = header_buttons

        logger.debug(
            f"Listando {len(operations_page)} operaciones de {paginator.count} total (readonly: {is_readonly})"
        )
        return context


# Vista para ver detalles de una operación en modo solo lectura
class OperacionViewDetailView(OperacionModelViewMixin, OperacionTemplateMixin):
    """
    Vista para ver detalles de una operación en modo solo lectura.
    Utiliza el mismo template que el formulario pero con campos deshabilitados.
    """

    template_name = "formularios/operacion_readonly.html"
    titulo = "Detalles de Operación"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener la instancia
        self.object = self.get_object()
        tipo_operacion = self.kwargs.get("tipo_operacion")

        # Crear un formulario con los datos de la instancia pero deshabilitado
        form_class = create_operacion_form(tipo_operacion)
        form = form_class(instance=self.object)

        # Deshabilitar todos los campos
        for field_name, field in form.fields.items():
            field.disabled = True
            # Añadir clase visual para campos deshabilitados
            field.widget.attrs["class"] += " bg-gray-100 cursor-not-allowed"

        context["form"] = form
        context["is_readonly"] = True

        # Añadir botón para volver a la lista
        context["header_buttons"] = [
            self.get_back_button("operaciones:lista_operaciones"),
        ]

        return context


# Vista para editar una operación
class OperacionEditView(OperacionModelViewMixin, UpdateView, OperacionFormMixin):
    """
    Vista para editar una operación existente.
    Permite modificar los datos de una operación previamente creada.
    """

    template_name = "formularios/operacion.html"
    titulo = "Editar Operación"
    boton_texto = "Actualizar Operación"

    def dispatch(self, request, *args, **kwargs):
        # Verificar si la solicitud ya fue enviada
        if hasattr(self, "base_request") and self.base_request.send_at is not None:
            messages.error(
                request, "No se puede editar una operación de una solicitud ya enviada."
            )
            return redirect(
                "operaciones:lista_operaciones", uuid=str(self.base_request.uuid)
            )
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        tipo_operacion = self.kwargs.get("tipo_operacion")
        logger.debug(
            f"Obteniendo formulario para edición de operación tipo: {tipo_operacion}"
        )
        return create_operacion_form(tipo_operacion)

    def form_valid(self, form):
        logger.info(
            f"Actualizando operación ID: {self.object.id}, tipo: {self.kwargs.get('tipo_operacion')}"
        )
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Operación actualizada correctamente.")
        return reverse(
            "operaciones:lista_operaciones",
            kwargs={"uuid": str(self.base_request.uuid)},
        )

    def get_header_buttons(self):
        return [self.get_back_button("operaciones:lista_operaciones")]


# Vista para eliminar una operación
class OperacionDeleteView(OperacionModelViewMixin, DeleteView, OperacionFormMixin):
    """
    Vista para eliminar una operación existente.
    Solicita confirmación antes de eliminar.
    """

    template_name = "formularios/operacion_confirm_delete.html"
    titulo = "Eliminar operación"
    boton_texto = "Eliminar"

    def dispatch(self, request, *args, **kwargs):
        # Verificar si la solicitud ya fue enviada
        if hasattr(self, "base_request") and self.base_request.send_at is not None:
            messages.error(
                request,
                "No se puede eliminar una operación de una solicitud ya enviada.",
            )
            return redirect(
                "operaciones:lista_operaciones", uuid=str(self.base_request.uuid)
            )
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        logger.info(
            f"Eliminando operación ID: {self.object.id}, tipo: {self.kwargs.get('tipo_operacion')}"
        )
        self.object.delete()
        messages.success(self.request, "Operación eliminada correctamente.")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "operaciones:lista_operaciones",
            kwargs={"uuid": str(self.base_request.uuid)},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = reverse(
            "operaciones:lista_operaciones",
            kwargs={"uuid": str(self.base_request.uuid)},
        )
        return context

    def get_header_buttons(self):
        return [self.get_back_button("operaciones:lista_operaciones")]


# Vista para previsualizar operaciones serializadas
class PrevisualizarOperacionesView(OperacionTemplateMixin):
    """
    Vista para previsualizar operaciones antes de enviar.
    Genera una representación JSON y un Excel para revisión.
    """

    template_name = "listados/preview.html"

    def get(self, request, *args, **kwargs):
        base_instance = self.base_request

        # Verificar si la solicitud ya fue enviada
        is_readonly = base_instance.send_at is not None

        operations = SessionService.get_operations_models(request)

        logger.info(
            f"Generando previsualización para solicitud {base_instance.uuid} con {len(operations)} operaciones"
        )

        preview_service = SolicitudPreviewService(base_instance, operations)
        success = preview_service.generar_preview()
        if not success:
            logger.warning(
                f"Intento de previsualizar solicitud {base_instance.uuid} sin operaciones"
            )
            messages.error(request, "No hay operaciones para enviar.")
            return redirect(
                "operaciones:lista_operaciones", uuid=str(base_instance.uuid)
            )

        logger.debug(
            f"Previsualización generada exitosamente para solicitud {base_instance.uuid}"
        )
        self.formatted_json = preview_service.formatted_json
        self.mailto_link = preview_service.mailto_link
        self.excel_url = preview_service.generar_excel()
        self.is_readonly = is_readonly
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formatted_json"] = self.formatted_json
        context["mailto_link"] = self.mailto_link
        context["excel_link"] = self.excel_url
        context["is_readonly"] = getattr(self, "is_readonly", False)

        # Configurar los botones según el estado
        header_buttons = []

        # Agregar botón de regreso (siempre presente)
        header_buttons.append(self.get_back_button("operaciones:lista_operaciones"))

        # Agregar botón de envío solo si no está en modo solo lectura
        if not getattr(self, "is_readonly", False):
            header_buttons.append(
                {
                    "id": "enviarSolicitud",
                    "href": reverse(
                        "operaciones:enviar_operaciones",
                        kwargs={"uuid": str(self.base_request.uuid)},
                    ),
                    "label": "Enviar Solicitud",
                    "icon": "fas fa-paper-plane",
                    "color": "success",
                }
            )

        context["header_buttons"] = header_buttons

        # Si está en modo solo lectura, agregar información de cuándo se envió
        if getattr(self, "is_readonly", False):
            context["send_date"] = self.base_request.send_at

        return context


# Vista para enviar operaciones serializadas
import logging


logger = logging.getLogger("operaciones")


class EnviarOperacionesView(BaseRequestMixin, View):
    """
    Vista para enviar operaciones serializadas al servicio SSN.
    Maneja el proceso de envío, mensajes de resultado y redirecciones.
    """

    def get(self, request, *args, **kwargs):
        base_instance = self.base_request
        operations = SessionService.get_operations_models(request)

        # Determinar si permitimos envío vacío (solo para solicitudes semanales)
        allow_empty = False
        if not operations:
            if base_instance.tipo_entrega == "Semanal":
                allow_empty = True
                logger.info(
                    f"Envío vacío permitido para solicitud semanal {base_instance.uuid}"
                )
            else:
                logger.warning(
                    f"Intento de enviar solicitud {base_instance.uuid} sin operaciones"
                )
                messages.error(request, "No hay operaciones para enviar.")
                return redirect(
                    "operaciones:lista_operaciones", uuid=str(base_instance.uuid)
                )

        logger.info(
            f"Enviando solicitud {base_instance.uuid} "
            f"con {len(operations)} operaciones "
            f"(allow_empty={allow_empty}). "
            f"Usuario: {request.user.username if request.user.is_authenticated else 'Anónimo'}"
        )

        sender = SolicitudSenderService(base_instance, operations)
        try:
            # Pasamos el flag allow_empty al servicio
            response_data, status_code = sender.enviar(allow_empty=allow_empty)

            if 200 <= status_code < 300:
                logger.info(f"Envío exitoso para solicitud {base_instance.uuid}")
                return self.handle_success(request, base_instance, response_data)
            else:
                logger.error(
                    f"Error en envío para solicitud {base_instance.uuid}. Código: {status_code}"
                )
                return self.handle_error(request, base_instance, response_data)

        except Exception as e:
            logger.exception(
                f"Error inesperado durante el envío de solicitud {base_instance.uuid}: {e}"
            )
            messages.error(
                request, f"Error inesperado al enviar la solicitud: {str(e)}"
            )
            return redirect(
                "operaciones:lista_operaciones", uuid=str(base_instance.uuid)
            )

    def handle_success(self, request, base_instance, response_data):
        success_message = response_data.get(
            "message", "Solicitud enviada correctamente."
        )
        messages.success(request, success_message)

        SessionService.clear_operations(request)
        logger.info(f"Sesión limpiada tras envío exitoso de {base_instance.uuid}")

        self.add_recovery_link(request, base_instance)
        return redirect(self.get_success_url())

    def handle_error(self, request, base_instance, response_data):
        error_message = response_data.get(
            "message", "Error desconocido al enviar la solicitud."
        )
        messages.error(request, error_message)

        for err in response_data.get("errors", []):
            messages.error(request, err)

        return redirect("operaciones:lista_operaciones", uuid=str(base_instance.uuid))

    def add_recovery_link(self, request, base_instance):
        uuid_str = str(base_instance.uuid)
        link = reverse("operaciones:solicitud_base") + f"?recover_uuid={uuid_str}"
        messages.info(
            request,
            f"Para recuperar o modificar esta solicitud más tarde, "
            f"use este <a href='{link}' class='text-blue-500 underline'>enlace</a>.",
        )

    def get_success_url(self):
        if getattr(settings, "HOME_URL", None):
            return settings.HOME_URL
        return reverse("operaciones:solicitud_base")


# Vista para listar todas las solicitudes base
class BaseRequestListView(PaginationMixin, StandaloneTemplateMixin):
    """
    Vista para listar todas las solicitudes base existentes.
    Muestra una tabla con las solicitudes y su estado.
    """

    template_name = "listados/lista_solicitudes.html"
    titulo = "Listado de Solicitudes"

    def get_header_buttons(self):
        """
        Define los botones del encabezado para la vista de listado de solicitudes.
        """
        return [
            {
                "href": reverse("operaciones:solicitud_base"),
                "label": "Nueva Solicitud",
                "icon": "fas fa-plus",
                "color": "primary",
            }
        ]

    def get_context_data(self, **kwargs):
        """
        Enriquece el contexto con la lista de solicitudes paginada.
        """
        context = super().get_context_data(**kwargs)

        # Limpiar la sesión actual
        SessionService.clear_base_request(self.request)
        SessionService.clear_operations(self.request)

        logger.debug("Obteniendo todas las solicitudes base")
        solicitudes = (
            BaseRequestModel.objects.all()
        )  # Ya vienen ordenadas por -created_at revisar model
        solicitudes_page, paginator = self.paginate_queryset(solicitudes)

        context["solicitudes"] = solicitudes_page
        context["paginator"] = paginator

        logger.debug(
            f"Listando {len(solicitudes_page)} solicitudes de {paginator.count} total"
        )
        return context
