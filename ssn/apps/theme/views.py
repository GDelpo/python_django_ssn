from django.conf import settings
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """
    Vista principal para la página de inicio del sistema de operaciones financieras.
    """

    template_name = "home/index.html"
    title = "Inicio | Sistema de Operaciones SSN"

    # --- Métodos ---
    def get_title(self):
        return self.title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Añadir el título al contexto
        context["title"] = self.get_title()

        # Definir los pasos del proceso
        context["pasos"] = [
            {
                "numero": 1,
                "titulo": "Crear Solicitud Base",
                "descripcion": "Inicie una nueva solicitud configurando el tipo de entrega y cronograma.",
                "icono": "fas fa-file-alt",
                "url": "operaciones:solicitud_base",
            },
            {
                "numero": 2,
                "titulo": "Agregar Operaciones",
                "descripcion": "Añada las operaciones financieras (compras, ventas, canjes o plazos fijos) a la solicitud.",
                "icono": "fas fa-plus-circle",
                "url": None,
            },
            {
                "numero": 3,
                "titulo": "Revisar Solicitud",
                "descripcion": "Verifique todas las operaciones antes de enviarlas a la SSN.",
                "icono": "fas fa-search",
                "url": None,
            },
            {
                "numero": 4,
                "titulo": "Enviar a SSN",
                "descripcion": "Transmita las operaciones validadas a la Superintendencia de Seguros de la Nación.",
                "icono": "fas fa-paper-plane",
                "url": None,
            },
        ]

        # Añadir correo de soporte desde settings
        context["support_email"] = settings.SUPPORT_EMAIL

        return context
