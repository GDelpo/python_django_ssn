from django import template

register = template.Library()


@register.inclusion_tag("componentes/link_button.html")
def link_button(href, label=None, icon=None, color="secondary", size="md", id=None):
    """
    Prepara un contexto seguro y completo para el componente de botón.
    Acepta argumentos por palabra clave y establece valores por defecto.
    """
    return {
        "href": href,
        "label": label,
        "icon": icon,
        "color": color,
        "size": size,
        "id": id,
    }
