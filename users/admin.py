### Import objects from wagtail admin
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from django.contrib import admin
# Import models from the app, polarrr  (.models means to get the models.py in the same directory as this file)
from .models import *
# Register your models here.


#########################################################################################
#### Admin settings for custom user profile

class UserProfileAdmin(ModelAdmin):

    model = UserProfile
    menu_label = 'User Profiles'
    menu_icon = "user"
    menu_order = 201
    add_to_settings_menu = True
    exclude_from_explorer = False
    list_display = ('user_name','full_name','gdpr','is_verified')
    search_fields = ('full_name','title')
    list_filter = ('is_verified','gdpr',)
    #actions = [make_verified,make_unverified]

    def user_name(self,obj):
        return obj.user.username

modeladmin_register(UserProfileAdmin)