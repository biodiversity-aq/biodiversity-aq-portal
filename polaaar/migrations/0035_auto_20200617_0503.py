# Generated by Django 2.2.12 on 2020-06-17 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polaaar', '0034_auto_20200615_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailfile',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='mailfile',
            name='document',
            field=models.FileField(blank=True, null=True, upload_to='polaaar/uploads/'),
        ),
        migrations.AlterField(
            model_name='projectfiles',
            name='files',
            field=models.FileField(blank=True, null=True, upload_to='polaaar/project_files/'),
        ),
    ]
