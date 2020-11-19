# accounts/views.py

from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import ugettext as _

from biodiversity.decorators import verify_recaptcha
from .models import UserProfile
from .email import *
from .forms import CustomUserCreationForm


@verify_recaptcha
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid() and request.recaptcha_is_valid:
            user = form.save()
            send_activation_email(request, user)
            return redirect(reverse('accounts:registered'))
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


def PasswordchangeDone(request):
    return render(request, 'registration/password_change_done.html')
