# accounts/views.py
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

import json
import urllib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as django_views
from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import ugettext as _

from .models import UserProfile
from .email import *
from .forms import CustomUserCreationForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
     
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {             
                'secret': settings.RECAPTCHA_PRIVATE_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req =  urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
#             ''' End reCAPTCHA validation '''
                                                                                                                
            #result=True
            if result['success']:#result==True:#
                user = form.save()
                send_activation_email(request, user)
                send_verification_email(request)
                
                messages.info(
                    request, _(
                        "We have sent you an email to %(email)s "
                        "so you can activate your account!") % {'email': form.cleaned_data['email']})

                           
                return redirect(reverse('accounts:registered'))

            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def registration_activation(request, pk, token):
    user = get_object_or_404(UserProfile, pk=pk)
    activation = UserActivationTokenGenerator()

    if activation.is_valid(user, token):
        user.is_active = True
        user.save()
        messages.info(request, _("Your account has been activated!"))

    return redirect(reverse('accounts:authenticated'))


def authenticated(request):
    return render(request, 'registration/authenticated.html')

def registered(request):
    return render(request, 'registration/registration_success.html')






