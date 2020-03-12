# Generated by Django 2.2.5 on 2020-02-11 12:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.core.models
import wagtail.images.blocks
import wagtail.images.models
import wagtail.search.index


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
        ('home', '0008_auto_20200206_0711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detailpage',
            name='body',
            field=wagtail.core.fields.StreamField([('insert_html', wagtail.core.blocks.RawHTMLBlock(help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element', required=False)), ('paragraph', wagtail.core.blocks.RichTextBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False))], blank=True),
        ),

    ]