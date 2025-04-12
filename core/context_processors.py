from django.conf import settings

def company_settings(request):
    """
    Add company settings to the template context
    """
    return {
        'COMPANY_NAME': settings.COMPANY_NAME,
    }
