from django.urls import path

from .views import (
    BaseRequestFormView,
    BaseRequestListView,
    EnviarOperacionesView,
    OperacionCreateView,
    OperacionDeleteView,
    OperacionEditView,
    OperacionViewDetailView,
    OperationTableView,
    PrevisualizarOperacionesView,
    SolicitudResponseDetailView,
    TipoOperacionFormView,
)

app_name = "operaciones"

urlpatterns = [
    # Inicio de solicitud base: aquí se crea la solicitud y se genera el UUID
    path("", BaseRequestFormView.as_view(), name="solicitud_base"),
    # Selección del tipo de operación (se pasa el uuid de la solicitud)
    path(
        "<uuid:uuid>/nueva/",
        TipoOperacionFormView.as_view(),
        name="seleccion_tipo_operacion",
    ),
    # Crear nueva operación
    path(
        "<uuid:uuid>/crear/<str:tipo_operacion>/",
        OperacionCreateView.as_view(),
        name="crear_operacion",
    ),
    # Editar operación
    path(
        "<uuid:uuid>/editar/<str:tipo_operacion>/<int:pk>/",
        OperacionEditView.as_view(),
        name="editar_operacion",
    ),
    # Eliminar operación
    path(
        "<uuid:uuid>/eliminar/<str:tipo_operacion>/<int:pk>/",
        OperacionDeleteView.as_view(),
        name="eliminar_operacion",
    ),
    # Ver detalles de operación (modo solo lectura)
    path(
        "<uuid:uuid>/ver/<str:tipo_operacion>/<int:pk>/",
        OperacionViewDetailView.as_view(),
        name="ver_operacion",
    ),
    # Listado de operaciones
    path("<uuid:uuid>/all/", OperationTableView.as_view(), name="lista_operaciones"),
    # Revisar operaciones serializadas
    path(
        "<uuid:uuid>/preview/",
        PrevisualizarOperacionesView.as_view(),
        name="preview_operaciones",
    ),
    # Enviar operaciones serializadas
    path(
        "<uuid:uuid>/enviar/",
        EnviarOperacionesView.as_view(),
        name="enviar_operaciones",
    ),
    # Listado de todas las solicitudes base
    path("solicitudes/", BaseRequestListView.as_view(), name="lista_solicitudes"),
    # Detalle de una respuesta generada
    path(
        "solicitudes/respuesta/<int:pk>/",
        SolicitudResponseDetailView.as_view(),
        name="detalle_respuesta",
    ),
]
