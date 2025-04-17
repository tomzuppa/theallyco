from datetime import datetime

def current_year(request):
    """
    Adds the current year to the template context.
    """
    return {
            #variable of current year
        'current_year': datetime.now().year
    }
