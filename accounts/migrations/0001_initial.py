# Generated by Django 2.2.5 on 2019-11-27 23:42

import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('full_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='fullname')),
                ('timezone', models.CharField(blank=True, default='UTC', max_length=32, null=True, verbose_name='time zone')),
                ('is_active', models.BooleanField(default=False, verbose_name='activated')),
                ('is_verified', models.BooleanField(default=False, help_text='Designates whether the user has verified his account by email or by other means. Un-select this to let the user activate his account.', verbose_name='verified')),
                ('position', models.CharField(blank=True, max_length=100, null=True)),
                ('institution', models.CharField(blank=True, max_length=100, null=True)),
                ('resident_country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('home_country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('introduction', models.TextField(blank=True, max_length=1500, null=True)),
                ('gdpr', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=True)),
                ('email_contact', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User profile',
                'verbose_name_plural': 'user profiles',
            },
        ),
    ]
