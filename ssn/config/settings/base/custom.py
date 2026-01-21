import os

from decouple import config

# --- SSN Client Configuration ---
# Usamos decouple directamente, sin parámetros inventados.
SSN_API_USERNAME = config("SSN_API_USERNAME")
SSN_API_PASSWORD = config("SSN_API_PASSWORD")
SSN_API_CIA = config("SSN_API_CIA")
SSN_API_BASE_URL = config("SSN_API_BASE_URL")
SSN_API_MAX_RETRIES = config("SSN_API_MAX_RETRIES", default=3, cast=int)
SSN_API_RETRY_DELAY = config("SSN_API_RETRY_DELAY", default=5, cast=int)
SSN_API_ENABLED = config("SSN_API_ENABLED", default=True, cast=bool)
SSN_API_VERIFY_SSL = config("SSN_API_VERIFY_SSL", default=True, cast=bool)  # False para test con cert self-signed

# --- Otras configuraciones ---
PREVIEW_MAX_AGE_MINUTES = config("PREVIEW_MAX_AGE_MINUTES", default=5, cast=int)
LOGGING_APPS = ["operaciones", "ssn_client"]
SUPPORT_EMAIL = config("SUPPORT_EMAIL", default="soporte@compania.com")

# --- Configuraciones de Terceros ---
TAILWIND_APP_NAME = "theme"
INTERNAL_IPS = ["127.0.0.1"]
NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd" if os.name == "nt" else "/usr/bin/npm"
REST_FRAMEWORK = {"DEFAULT_THROTTLE_RATES": {"anon": "100/day", "user": "1000/day"}}

# --- Configuración de la Compañía ---
COMPANY_NAME = config("COMPANY_NAME", default="Nombre Compañía")
COMPANY_WEBSITE = config("COMPANY_WEBSITE", default="https://www.compania.com")
COMPANY_LOGO_URL = config(
    "COMPANY_LOGO_URL", default="https://www.compania.com/logo.png"
)
COMPANY_FAVICON_URL = config(
    "COMPANY_FAVICON_URL", default="https://www.compania.com/favicon.ico"
)
