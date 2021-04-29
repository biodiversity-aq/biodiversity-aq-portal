# Generated by Django 2.2.14 on 2021-03-24 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polaaar', '0051_auto_20210323_0947'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='projectmetadata',
            options={'ordering': ['-start_date'], 'verbose_name': 'Project metadata', 'verbose_name_plural': 'Project metadata'},
        ),
        migrations.AlterField(
            model_name='environment',
            name='env_text_value',
            field=models.CharField(blank=True, help_text='http://rs.tdwg.org/dwc/terms/measurementValue', max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='sequences',
            name='seqData_numberOfBases',
            field=models.BigIntegerField(blank=True, help_text='The number of bases predicted in a sequenced sample', null=True),
        ),
        migrations.AlterField(
            model_name='sequences',
            name='seqData_numberOfSequences',
            field=models.BigIntegerField(blank=True, help_text='the number of sequences in a sample or folder', null=True),
        ),
    ]
