from __future__ import unicode_literals
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings

from django_countries.fields import CountryField

from .managers import CustomUserManager

BOOLEAN_YN = (
(True, u'Yes'),
(False, u'No'),  
)

class UserProfile(AbstractUser):
    #pass
    # add additional fields in here
    #user = models.OneToOneField(
    #    settings.AUTH_USER_MODEL,
    #    verbose_name=_("profile"),        
    #    on_delete=models.CASCADE)

    full_name = models.CharField(_("fullname"),max_length=100,blank=True,null=True)
    timezone = models.CharField(_("time zone"), max_length=32, default='UTC',null=True,blank=True)

    is_active = models.BooleanField(_("activated"),default=False)
    is_verified = models.BooleanField(
        _('verified'), default=False,
        help_text=_(
            'Designates whether the user has verified his '
            'account by email or by other means. Un-select this '
            'to let the user activate his account.'))

    position = models.CharField(max_length=100,null=True,blank=True)    
    institution = models.CharField(max_length=100, null=True, blank=True)
    
    resident_country = CountryField(null=True, blank=True)
    home_country = CountryField(null=True, blank=True)
      
    introduction = models.TextField(max_length=1500,blank=True,null=True)

    gdpr = models.BooleanField(default=True,choices=BOOLEAN_YN)    
    email_contact = models.BooleanField(default=True,choices=BOOLEAN_YN)

   
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def __str__(self):
        return self.first_name + ' ' + self.last_name


    class Meta:
        verbose_name = _("User profile")
        verbose_name_plural = _("user profiles")

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.is_administrator = True
        
        self.full_name = self.first_name + ' ' + self.last_name

        super(UserProfile, self).save(*args, **kwargs)

    #def get_absolute_url(self):
    #    return reverse(
    #        'spirit:user:detail',
    #        kwargs={'pk': self.user.pk, 'slug': self.slug})

     