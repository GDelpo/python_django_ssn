from .paths import get_build_config
import os

# --- SSN Client Configuration ---
SSN_API_USERNAME = get_build_config("SSN_API_USERNAME", build_value="build_user")
SSN_API_PASSWORD = get_build_config("SSN_API_PASSWORD", build_value="build_pass")
SSN_API_CIA = get_build_config("SSN_API_CIA", build_value="build_cia")
SSN_API_BASE_URL = get_build_config(
    "SSN_API_BASE_URL", build_value="https://example.com"
)
SSN_API_MAX_RETRIES = get_build_config("SSN_API_MAX_RETRIES", default=3, cast=int)
SSN_API_RETRY_DELAY = get_build_config("SSN_API_RETRY_DELAY", default=5, cast=int)

# --- Otras configuraciones personalizadas ---
PREVIEW_MAX_AGE_MINUTES = get_build_config(
    "PREVIEW_MAX_AGE_MINUTES", default=5, cast=int
)
LOGGING_APPS = ["operaciones", "ssn_client"]
SUPPORT_EMAIL = get_build_config("SUPPORT_EMAIL", default="soporte@compania.com")

# --- Configuraciones de Terceros (Tailwind, DRF) ---
TAILWIND_APP_NAME = "theme"
INTERNAL_IPS = ["127.0.0.1"]
NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd" if os.name == "nt" else "/usr/bin/npm"
REST_FRAMEWORK = {"DEFAULT_THROTTLE_RATES": {"anon": "100/day", "user": "1000/day"}}

# --- Configuración de la Compañía ---
COMPANY_NAME = get_build_config("COMPANY_NAME", default="Nombre Compañía")
COMPANY_WEBSITE = get_build_config("COMPANY_WEBSITE", default="https://www.compania.com")
COMPANY_LOGO_URL = get_build_config(
    "COMPANY_LOGO_URL", default="https://www.compania.com/logo.png"
)