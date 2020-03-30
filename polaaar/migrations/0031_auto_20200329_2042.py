# Generated by Django 2.2.5 on 2020-03-29 19:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polaaar', '0030_auto_20200328_2110'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventhierarchy',
            options={'ordering': ['event_hierarchy_name'], 'verbose_name': 'Event hierarchy', 'verbose_name_plural': 'Event hierarchy'},
        ),
        migrations.AlterModelOptions(
            name='geog_location',
            options={'ordering': ['name'], 'verbose_name': 'Geography', 'verbose_name_plural': 'Geographic Locations'},
        ),
        migrations.AlterModelOptions(
            name='package',
            options={'ordering': ['name'], 'verbose_name': 'MiXS packages', 'verbose_name_plural': 'MiXS packages'},
        ),
        migrations.AlterModelOptions(
            name='projectmetadata',
            options={'ordering': ['project_name'], 'verbose_name': 'Project metadata', 'verbose_name_plural': 'Project metadata'},
        ),
    ]