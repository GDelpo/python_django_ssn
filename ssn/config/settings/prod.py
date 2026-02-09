from decouple import Csv, config

from .base import *

# --- CONFIGURACIÓN DE PRODUCCIÓN ---
DEBUG = config("DEBUG", default=False, cast=bool)
SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

# CSRF Trusted Origins
# Automatically builds the list from SSL_DOMAIN and SSL_IP.
# Works for both Nginx mode (HTTPS ports) and Traefik mode (HTTP/HTTPS).
_csrf_origins = []

_ssl_domain = config("SSL_DOMAIN", default="")
_ssl_ip = config("SSL_IP", default="")
_nginx_https = config("NGINX_PORT_HTTPS", default="443")
if _ssl_domain:
    _csrf_origins.append(f"https://{_ssl_domain}:{_nginx_https}")
    _csrf_origins.append(f"https://{_ssl_domain}")
    _csrf_origins.append(f"http://{_ssl_domain}")
if _ssl_ip:
    _csrf_origins.append(f"https://{_ssl_ip}:{_nginx_https}")
    _csrf_origins.append(f"http://{_ssl_ip}")

# Allow extra origins via env (comma-separated)
_extra_origins = config("CSRF_EXTRA_ORIGINS", default="", cast=Csv())
_csrf_origins.extend([o for o in _extra_origins if o])

CSRF_TRUSTED_ORIGINS = _csrf_origins

# Cargar configuración de Logging para producción
LOGGING = get_logging_config(debug_mode=DEBUG, logs_dir=LOGS_DIR, apps=LOGGING_APPS)
