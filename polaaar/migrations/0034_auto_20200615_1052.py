# Generated by Django 2.2.12 on 2020-06-15 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polaaar', '0033_auto_20200610_0432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectfiles',
            name='files',
            field=models.FileField(blank=True, null=True, upload_to='polaaar/'),
        ),
    ]
