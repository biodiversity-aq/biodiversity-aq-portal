# Generated by Django 2.2.5 on 2020-02-24 13:17

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0018_auto_20200224_1013'),
    ]

    operations = [
        migrations.AddField(
            model_name='overviewpage',
            name='cover',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='home.CustomImage'),
        ),
        migrations.AddField(
            model_name='overviewpage',
            name='short_description',
            field=wagtail.core.fields.RichTextField(blank=True, help_text='A one line description of the page that will appear in overview page.', null=True),
        ),
        migrations.AddField(
            model_name='redirectdummypage',
            name='cover',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='home.CustomImage'),
        ),
        migrations.AddField(
            model_name='redirectdummypage',
            name='short_description',
            field=wagtail.core.fields.RichTextField(blank=True, help_text='A one line description of the page that will appear in overview page.', null=True),
        ),
    ]
