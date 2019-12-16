from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import UserProfile

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = UserProfile
    list_display = ['email', 'username','full_name','gdpr','email_contact','is_verified','is_active']

admin.site.register(UserProfile, CustomUserAdmin)


