from decouple import Csv, config

from .base import *

# --- CONFIGURACIÓN DE PRODUCCIÓN ---
DEBUG = config("DEBUG", default=False, cast=bool)
SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

CSRF_TRUSTED_ORIGINS = [
    f"https://{config('SSL_DOMAIN')}:{config('NGINX_PORT_HTTPS')}",
    f"https://{config('SSL_IP')}:{config('NGINX_PORT_HTTPS')}",
]

# Cargar configuración de Logging para producción
LOGGING = get_logging_config(debug_mode=DEBUG, logs_dir=LOGS_DIR, apps=LOGGING_APPS)
