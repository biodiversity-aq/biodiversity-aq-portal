# Generated by Django 2.2.5 on 2020-03-21 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polaaar', '0012_auto_20200321_1317'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_metadata',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='polaaar.Metadata'),
        ),
    ]
