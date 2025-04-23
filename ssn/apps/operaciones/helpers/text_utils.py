import re


def camel_to_title(text):
    """
    Convierte un texto en formato camelCase a Title Case.

    Args:
        text (str): Texto en formato camelCase.

    Returns:
        str: Texto formateado en Title Case.

    Example:
        >>> camel_to_title("nombreUsuario")
        'Nombre Usuario'
    """
    return re.sub(r"(?<!^)(?=[A-Z])", " ", text).title()


def to_camel_case(snake_str):
    """
    Convierte un string en formato snake_case a camelCase.
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])
