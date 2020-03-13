from django.urls import path
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = "accounts"
urlpatterns = [
    path('registered/',views.registered,name='registered'),
    path('authenticated/', views.authenticated,name='authenticated'),
    path('register/', views.register, name='register'),

    url(r'^activation/(?P<pk>[0-9]+)/(?P<token>[0-9A-Za-z_\-\.]+)/$',
        views.registration_activation,
        name='registration-activation'),

    path('password-change/', 
         auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'),
         {'post_change_redirect':'password_change_done'},
         name='password_change'),

    #path('password-change/done/', 
    #     views.PasswordchangeDone,
    #     name='password_change_done')
    
    path('password_change/done/', 
         auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'),
         name='password_change_done')



]