import logging
import uuid

from django.db import models
from rest_framework import serializers

from .models import BaseRequestModel, TipoEspecie

# Configuración del logger
logger = logging.getLogger("operaciones")


def transform_representation(data):
    """
    Transforma las claves de un diccionario a camelCase.
    Si el valor es None, lo reemplaza por cadena vacía.
    Convierte UUIDs a strings.

    Args:
        data (dict): Diccionario con datos a transformar

    Returns:
        dict: Diccionario con claves en camelCase y valores transformados
    """
    from .helpers import to_camel_case

    transformed = {}
    for k, v in data.items():
        key = to_camel_case(k)
        if v is None:
            transformed[key] = ""
        elif isinstance(v, uuid.UUID):
            transformed[key] = str(v)
        else:
            transformed[key] = v

    logger.debug(f"Transformación camelCase completada: {len(data)} campos procesados")
    return transformed


class CustomDateField(serializers.DateField):
    """
    Campo de fecha personalizado que formatea las fechas al formato DDMMYYYY.
    Útil para sistemas externos que requieren este formato específico.
    """

    def to_representation(self, value):
        """
        Convierte la fecha al formato DDMMYYYY.

        Args:
            value (date): Fecha a formatear

        Returns:
            str: Fecha formateada o None
        """
        formatted = value if value else None
        logger.debug(f"Fecha formateada: {value} -> {formatted}")
        return formatted

class CustomBooleanField(serializers.BooleanField):
    """
    Campo booleano personalizado que convierte valores booleanos a "1" o "0" (string).
    Utilizado para compatibilidad con servicios externos que esperan strings.
    """

    def to_representation(self, value):
        """
        Convierte el valor booleano a "1" o "0".

        Args:
            value (bool): Valor booleano a formatear

        Returns:
            str: "1" para True, "0" para False
        """
        formatted = "1" if value else "0"
        logger.debug(f"Valor booleano formateado: {value} -> {formatted}")
        return formatted
    
class CamelCaseModelSerializer(serializers.ModelSerializer):
    """
    Serializador base que transforma la representación de los datos a camelCase.
    Además, redefine los campos de fecha para utilizar CustomDateField.
    """

    def to_representation(self, instance):
        """
        Personaliza la representación de los datos, aplicando reglas específicas
        para ciertos tipos de campos y transformando las claves a camelCase.

        Args:
            instance: Instancia del modelo a serializar

        Returns:
            dict: Datos serializados con claves en camelCase
        """
        original = super().to_representation(instance)

        # Formatear cant_especies si existe en el modelo y en los datos serializados
        if (
            hasattr(instance, "cant_especies")
            and "cant_especies" in original
            and original["cant_especies"] is not None
        ):
            # Verificar si tiene el campo tipo_especie y si no es FCI
            if (
                hasattr(instance, "tipo_especie")
                and instance.tipo_especie != TipoEspecie.FONDOS_COMUNES_DE_INVERSIÓN
            ):
                # Convertir a entero para tipos de especie que no son FCI
                original["cant_especies"] = int(float(original["cant_especies"]))
                logger.debug(
                    f"Cantidad de especies convertida a entero: {original['cant_especies']}"
                )

        transformed = transform_representation(original)

        if hasattr(instance, "pk"):
            logger.debug(
                f"Serialización completada para instancia ID: {instance.pk}, modelo: {instance.__class__.__name__}"
            )

        return transformed

    def build_standard_field(self, field_name, model_field):
        """
        Personaliza la construcción de campos estándar, reemplazando
        campos de fecha por CustomDateField.

        Args:
            field_name: Nombre del campo
            model_field: Campo del modelo

        Returns:
            tuple: (clase del campo, argumentos del campo)
        """
        field_class, field_kwargs = super().build_standard_field(
            field_name, model_field
        )
        if isinstance(model_field, (models.DateField, models.DateTimeField)):
            field_class = CustomDateField
            logger.debug(f"Campo de fecha personalizado aplicado: {field_name}")
        return field_class, field_kwargs


class BaseModelSerializer(CamelCaseModelSerializer):
    """
    Serializador para BaseRequestModel.
    Se excluyen campos específicos para evitar exponerlos en la serialización.
    """

    class Meta:
        model = BaseRequestModel
        exclude = ["uuid", "send_at", "created_at"]


def create_model_serializer(tipo_operacion):
    """
    Crea dinámicamente un serializador para el modelo correspondiente
    al tipo de operación especificado.

    Args:
        tipo_operacion (str): Código del tipo de operación

    Returns:
        class: Clase de serializador específica para el tipo de operación

    Raises:
        ValueError: Si el tipo de operación no es válido
    """
    from .helpers import get_mapping_model

    logger.debug(f"Creando serializador para tipo de operación: {tipo_operacion}")

    mapping = get_mapping_model()
    model_class = mapping.get(tipo_operacion)

    if not model_class:
        logger.error(f"Tipo de operación no válida: {tipo_operacion}")
        raise ValueError(f"Tipo de operación no válida: {tipo_operacion}")

    class DynamicModelSerializer(CamelCaseModelSerializer):
        """
        Serializador dinámico para un tipo específico de operación.
        """

        class Meta:
            model = model_class
            exclude = ["id", "comprobante", "solicitud"]

    logger.debug(f"Serializador creado para modelo: {model_class.__name__}")
    return DynamicModelSerializer


def serialize_operations(base_instance, operations, pre_serialized=False):
    """
    Serializa una instancia base y las operaciones asociadas.

    Args:
        base_instance: Instancia del modelo base (BaseRequestModel)
        operations: Lista de operaciones a serializar (instancias reales de modelo)
        pre_serialized (bool): Indica si las operaciones ya están serializadas

    Returns:
        dict: Datos serializados con la instancia base y sus operaciones
    """
    logger.info(
        f"Serializando solicitud {base_instance.uuid} con {len(operations)} operaciones"
    )

    base_data = BaseModelSerializer(base_instance).data

    if pre_serialized:
        logger.debug("Usando operaciones pre-serializadas")
        base_data["operaciones"] = operations
    else:
        logger.debug("Serializando cada operación individualmente")
        serialized_ops = []

        for op in operations:
            try:
                tipo = getattr(op, "tipo_operacion", None)
                if tipo is None:
                    logger.warning(
                        f"No se encontró tipo_operacion para instancia {op}."
                    )
                    continue  # O podrías intentar deducir el tipo por el modelo

                serializer_class = create_model_serializer(tipo)
                serialized_data = serializer_class(op).data
                serialized_ops.append(serialized_data)
                logger.debug(f"Operación tipo {tipo} serializada correctamente")
            except Exception as e:
                logger.error(f"Error al serializar operación: {str(e)}")

        base_data["operaciones"] = serialized_ops
        logger.debug(f"Total de operaciones serializadas: {len(serialized_ops)}")

    return base_data
