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