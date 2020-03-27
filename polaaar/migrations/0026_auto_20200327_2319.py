# Generated by Django 2.2.5 on 2020-03-27 23:19

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polaaar', '0025_auto_20200327_1133'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectmetadata',
            name='project_file',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='/media/project_files'), upload_to=''),
        ),
        migrations.AlterField(
            model_name='event',
            name='collection_month',
            field=models.IntegerField(blank=True, choices=[(1, '01'), (2, '02'), (3, '03'), (4, '04'), (5, '05'), (6, '06'), (7, '07'), (8, '08'), (9, '09'), (10, '10'), (11, '11'), (12, '12')], null=True),
        ),
    ]
