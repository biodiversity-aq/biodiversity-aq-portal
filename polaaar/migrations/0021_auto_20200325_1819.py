# Generated by Django 2.2.5 on 2020-03-25 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polaaar', '0020_auto_20200324_2357'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sequences',
            name='environment',
        ),
        migrations.AddField(
            model_name='samplemetadata',
            name='environment',
            field=models.ManyToManyField(blank=True, to='polaaar.Environment'),
        ),
    ]
