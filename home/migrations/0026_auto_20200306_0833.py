# Generated by Django 2.2.5 on 2020-03-06 08:33

from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0025_auto_20200305_0921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detailpage',
            name='short_description',
            field=wagtail.core.fields.RichTextField(blank=True, help_text='A one line description of the page to help user discover this page.', null=True),
        ),
        migrations.AlterField(
            model_name='overviewpage',
            name='short_description',
            field=wagtail.core.fields.RichTextField(blank=True, help_text='A one line description of the page to help user discover this page.', null=True),
        ),
        migrations.AlterField(
            model_name='redirectdummypage',
            name='short_description',
            field=wagtail.core.fields.RichTextField(blank=True, help_text='A one line description of the page to help user discover this page.', null=True),
        ),
    ]
