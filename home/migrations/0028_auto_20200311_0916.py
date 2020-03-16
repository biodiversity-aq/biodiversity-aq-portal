# Generated by Django 2.2.5 on 2020-03-11 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0027_footer'),
    ]

    operations = [
        migrations.AddField(
            model_name='linkedbutton',
            name='external_url',
            field=models.URLField(blank=True, help_text='A valid url if the button is to link to an external page not managed via this CMS.', null=True),
        ),
        migrations.AlterField(
            model_name='linkedbutton',
            name='color',
            field=models.CharField(blank=True, default='btn-outline-white', help_text="Button class e.g. 'btn-primary'. Button classes available (free version only): https://bit.ly/3ctJtir", max_length=100, null=True),
        ),
    ]