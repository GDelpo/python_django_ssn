# Importa toda la configuración base que ya tienes
from .base import *

# Sobrescribe la configuración de la base de datos SOLO para este entorno
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_build.sqlite3",
    }
}

# Define un SECRET_KEY temporal para el build
SECRET_KEY = "dummy_secret_for_build_purposes_only"

# Desactiva configuraciones de seguridad que no aplican al build
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
