import os
import sys
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Añadir directorio de apps al path
APPS_DIR = BASE_DIR / "apps"
sys.path.insert(0, str(APPS_DIR))

# Directorios de Media, Static y Logs
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "/static/"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Lógica para detectar el entorno de build de Docker
IN_DOCKER_BUILD = os.environ.get("SECRET_KEY") == "dummy"

def get_build_config(key, default=None, build_value=None, cast=None):
    """
    Obtiene un valor de configuración, con manejo especial para entorno de construcción.
    """
    if IN_DOCKER_BUILD and build_value is not None:
        if cast is not None and build_value is not None:
            return cast(build_value)
        return build_value
    if cast is not None:
        return config(key, default=default, cast=cast)
    return config(key, default=default)
