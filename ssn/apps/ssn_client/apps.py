from django.apps import AppConfig
from django.conf import settings

from .clients import SsnService


class SsnClientConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ssn_client"
    ssn_client = None

    def ready(self):
        # Inicializamos el cliente singleton con los parámetros de settings
        SsnClientConfig.ssn_client = SsnService(
            username=settings.SSN_API_USERNAME,
            password=settings.SSN_API_PASSWORD,
            cia=settings.SSN_API_CIA,
            base_url=settings.SSN_API_BASE_URL,
            max_retries=settings.SSN_API_MAX_RETRIES,
            retry_delay=settings.SSN_API_RETRY_DELAY,
        )
