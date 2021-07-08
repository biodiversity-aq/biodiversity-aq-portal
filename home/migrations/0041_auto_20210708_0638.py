# Generated by Django 2.2.24 on 2021-07-08 06:38
from django.apps import apps
from django.db import migrations


def update_display_published_date(queryset):
    for page in queryset:
        page.displayed_publish_date = page.last_published_at.date()
        page.save()


def run_update_display_pub_date():
    """
    Update all children of BaseMenuPage (abstract class) so that displayed_publish_date == last_published_at
    """
    DetailPage = apps.get_model('home', 'DetailPage')
    OverviewPage = apps.get_model('home', 'OverviewPage')
    RedirectDummyPage = apps.get_model('home', 'RedirectDummyPage')
    update_display_published_date(DetailPage.objects.all())
    update_display_published_date(OverviewPage.objects.all())
    update_display_published_date(RedirectDummyPage.objects.all())


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0040_auto_20210625_1026'),
    ]

    operations = [
        migrations.RunPython(run_update_display_pub_date)
    ]
