# ssn/config/settings/dev.py
from .base import *
from decouple import config

# --- SOBREESCRIBIR PARA DESARROLLO ---
DEBUG = True
SECRET_KEY = config("SECRET_KEY", default="django-insecure-dev-key-para-desarrollo")
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "web"]

# Relajar seguridad para desarrollo
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0

# Cargar configuración de Logging para el modo DEBUG
LOGGING = get_logging_config(debug_mode=DEBUG, logs_dir=LOGS_DIR, apps=LOGGING_APPS)
