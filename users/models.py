from __future__ import unicode_literals


from django.db import models
from django.contrib import admin
from django.utils.translation import gettext as _
from django.utils.html import format_html
from django.conf import settings
from django.contrib.gis.gdal import *
#from djgeojson.fields import PointField
from django.contrib.gis.db import models

from django_countries.fields import CountryField

from polaaar.models import *


#### Custom user profile table

### Django's base user profile model only includes a few fields. We create a custom user profile
### that uses a one to one link to the base user model allowing us to add new fields. We can also
### use it to assign datasets to users which will give us the ability to control access

INSTITUTIONS = (
    ('gov','Government'),
    ('aca','Academic'),
    ('ind','Industry'),
    ('ngo','Non-Governmental'),
    ('fre','Freelance'),
    ('oth','Other')
    )

BOOLEAN_YN = (
(True, u'Yes'),
(False, u'No'),  
)



TITLES = ('Mr', 'Ms', 'Mrs', 'Miss', 'Dr', 'Prof')

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("profile"),
        related_name='st',
        on_delete=models.CASCADE)

    full_name = models.CharField(max_length=100,blank=True,null=True,
                                 help_text=_('The full name (first + last) of the user '
                                             'This does not have to be filled out on the back end '
                                             'It is generated from the USER table when you save '))
    is_administrator = models.BooleanField(_('administrator status'), default=False,
                                           help_text=_('Designates if the user is an adminstrator '
                                                       'with priviledges to access the admin side '
                                                       'of the site and alter data tables.'
                                                       ))
    is_verified = models.BooleanField(
        _('verified'), default=False,
        help_text=_(
            'Designates whether the user has verified his '
            'account by email or by other means. Un-select this '
            'to let the user activate his account.'))
    
    title = models.CharField(max_length=5, choices=zip(TITLES, TITLES), null=True, blank=True)
    position = models.CharField(max_length=100,null=True,blank=True)    
    institution = models.CharField(max_length=100, null=True, blank=True)    
    institution_type = models.CharField(max_length=60,null=True,blank=True,choices=INSTITUTIONS)    
    resident_country = CountryField(null=True, blank=True)
    home_country = CountryField(null=True, blank=True)    
    introduction = models.TextField(max_length=1500,blank=True,null=True)
    gdpr = models.BooleanField(default=True,choices=BOOLEAN_YN)    
    email_contact = models.BooleanField(default=True,choices=BOOLEAN_YN)

   
    parent_events_owned = models.ManyToManyField(_('polaaar.ParentEvent'),blank=True,
                                                 help_text=_('This indicates which parent event(s) '
                                                             'the user owns or has access to. '
                                                             'This can be granted by other users on the '
                                                             'front end. If a top-level event (e.g., project) '
                                                             'is selected, they will have access to all sub-events.'))


    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name
     
    class Meta:
        
        ordering = ['user__last_name']
        verbose_name = _("User profile")
        verbose_name_plural = _("User profiles")

    def save(self, *args, **kwargs):
        if self.user.is_superuser:
            self.is_administrator = True

        if self.is_administrator:
            self.is_moderator = True
        
        self.full_name = self.user.first_name + ' ' + self.user.last_name

        super(UserProfile, self).save(*args, **kwargs)


