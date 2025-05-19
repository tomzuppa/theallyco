from datetime import datetime
from django.conf import settings


def current_year(request):
    """
    Adds the current year to the template context.
    """
    return {
            #variable of current year
        'current_year': datetime.now().year
    }




def company_name(request):
    """
    ✅ Adds COMPANY_NAME to all template contexts.
    """
    return {
        'COMPANY_NAME': getattr(settings, 'COMPANY_NAME', 'Baobyte')
    }
