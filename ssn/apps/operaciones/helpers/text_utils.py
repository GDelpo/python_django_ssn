import json
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


def pretty_json(data):
    """
    Converts a Python object into a formatted JSON string with indentation for readability.
    Args:
        data (Any): The Python object to be serialized into JSON.
    Returns:
        str: A JSON-formatted string representation of the input data, indented for readability and preserving non-ASCII characters.
    """

    return json.dumps(data, indent=4, ensure_ascii=False)
