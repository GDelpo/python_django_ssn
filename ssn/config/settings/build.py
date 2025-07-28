from .base import *

# --- Sobrescribir para el entorno de BUILD ---

# 1. Base de datos SQLite
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_build.sqlite3",
    }
}

# 2. Clave secreta temporal
SECRET_KEY = "dummy_secret_for_build_purposes_only"

# 3. Relajar seguridad
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# 4. Definir valores "dummy" para las variables de `custom.py` que no tienen default
SSN_API_USERNAME = "build_user"
SSN_API_PASSWORD = "build_pass"
SSN_API_CIA = "build_cia"
SSN_API_BASE_URL = "https://build-example.com"