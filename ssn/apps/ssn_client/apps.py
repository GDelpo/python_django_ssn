from django.apps import AppConfig
from django.conf import settings
import sys
import os

from .clients import SsnService


class SsnClientConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ssn_client"
    ssn_client = None

    def ready(self):
        # Verificar si estamos en un comando de manejo no relacionado con el cliente
        management_commands = [
            "tailwind",
            "collectstatic",
            "makemigrations",
            "migrate",
            "shell",
        ]
        is_management_command = any(
            cmd in " ".join(sys.argv) for cmd in management_commands
        )

        # Verificar si estamos en fase de construcción con SECRET_KEY dummy
        is_build_env = os.environ.get("SECRET_KEY") in ["dummy", "nothing"]

        # Si estamos ejecutando ciertos comandos o en fase de construcción,
        # no inicializar el cliente
        if is_management_command or is_build_env:
            return

        try:
            # Intentar inicializar el cliente normalmente
            SsnClientConfig.ssn_client = SsnService(
                username=settings.SSN_API_USERNAME,
                password=settings.SSN_API_PASSWORD,
                cia=settings.SSN_API_CIA,
                base_url=settings.SSN_API_BASE_URL,
                max_retries=settings.SSN_API_MAX_RETRIES,
                retry_delay=settings.SSN_API_RETRY_DELAY,
            )
        except Exception as e:
            # Si hay un error, registrar el error
            import logging

            logger = logging.getLogger("ssn_client")
            logger.warning(f"No se pudo inicializar el cliente SSN: {str(e)}")
