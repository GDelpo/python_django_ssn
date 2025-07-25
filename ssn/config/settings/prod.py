from .base import *
from decouple import config, Csv

# --- CONFIGURACIÓN DE PRODUCCIÓN ---
DEBUG = False
SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

# Cargar configuración de Logging para producción
LOGGING = get_logging_config(debug_mode=DEBUG, logs_dir=LOGS_DIR, apps=LOGGING_APPS)
