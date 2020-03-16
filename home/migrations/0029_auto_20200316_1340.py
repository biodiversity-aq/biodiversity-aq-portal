# Generated by Django 2.2.5 on 2020-03-16 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0028_auto_20200311_0916'),
    ]

    operations = [
        migrations.AddField(
            model_name='detailpage',
            name='show_in_parent',
            field=models.BooleanField(blank=True, default=False, help_text='If true (checked) this page will appear in the bottom of parent page if parent page type is AppLandingPage or OverviewPage.', null=True),
        ),
        migrations.AddField(
            model_name='overviewpage',
            name='show_in_parent',
            field=models.BooleanField(blank=True, default=False, help_text='If true (checked) this page will appear in the bottom of parent page if parent page type is AppLandingPage or OverviewPage.', null=True),
        ),
        migrations.AddField(
            model_name='redirectdummypage',
            name='show_in_parent',
            field=models.BooleanField(blank=True, default=False, help_text='If true (checked) this page will appear in the bottom of parent page if parent page type is AppLandingPage or OverviewPage.', null=True),
        ),
    ]
