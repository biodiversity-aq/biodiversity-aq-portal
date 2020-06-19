from functools import wraps
from django.conf import settings

import requests


def verify_recaptcha(view_func):
    """
    Verify user's response to a reCAPTCHA challenge.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        request.recaptcha_is_valid = False
        if request.method == 'POST':
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': settings.RECAPTCHA_PRIVATE_KEY,
                'response': recaptcha_response
            }
            verify_url = 'https://www.google.com/recaptcha/api/siteverify'
            response = requests.post(verify_url, data=data)
            if response.status_code == 200:
                request.recaptcha_is_valid = response.json().get('success')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
