# Generated by Django 2.2.5 on 2019-11-03 11:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('polaaar', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, help_text='The full name (first + last) of the user This does not have to be filled out on the back end It is generated from the USER table when you save ', max_length=100, null=True)),
                ('is_administrator', models.BooleanField(default=False, help_text='Designates if the user is an adminstrator with priviledges to access the admin side of the site and alter data tables.', verbose_name='administrator status')),
                ('is_verified', models.BooleanField(default=False, help_text='Designates whether the user has verified his account by email or by other means. Un-select this to let the user activate his account.', verbose_name='verified')),
                ('title', models.CharField(blank=True, choices=[('Mr', 'Mr'), ('Ms', 'Ms'), ('Mrs', 'Mrs'), ('Miss', 'Miss'), ('Dr', 'Dr'), ('Prof', 'Prof')], max_length=5, null=True)),
                ('position', models.CharField(blank=True, max_length=100, null=True)),
                ('institution', models.CharField(blank=True, max_length=100, null=True)),
                ('institution_type', models.CharField(blank=True, choices=[('gov', 'Government'), ('aca', 'Academic'), ('ind', 'Industry'), ('ngo', 'Non-Governmental'), ('fre', 'Freelance'), ('oth', 'Other')], max_length=60, null=True)),
                ('resident_country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('home_country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('introduction', models.TextField(blank=True, max_length=1500, null=True)),
                ('gdpr', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=True)),
                ('email_contact', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=True)),
                ('parent_events_owned', models.ManyToManyField(blank=True, help_text='This indicates which parent event(s) the user owns or has access to. This can be granted by other users on the front end. If a top-level event (e.g., project) is selected, they will have access to all sub-events.', to='polaaar.ParentEvent')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='st', to=settings.AUTH_USER_MODEL, verbose_name='profile')),
            ],
            options={
                'verbose_name': 'User profile',
                'verbose_name_plural': 'User profiles',
                'ordering': ['user__last_name'],
            },
        ),
    ]
