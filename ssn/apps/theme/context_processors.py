from django.conf import settings


def company_info(request):
    """
    Agrega variables de configuración de la compañía al contexto de los templates.
    """
    return {
        "COMPANY_NAME": settings.COMPANY_NAME,
        "COMPANY_WEBSITE": settings.COMPANY_WEBSITE,
        "COMPANY_REGISTRATION_NUMBER": settings.SSN_API_CIA,
        "COMPANY_LOGO_URL": settings.COMPANY_LOGO_URL,
    }
