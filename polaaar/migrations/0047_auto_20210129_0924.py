# Generated by Django 2.2.14 on 2021-01-29 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polaaar', '0046_auto_20201204_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sequences',
            name='seqData_accessionNumber',
            field=models.CharField(blank=True, help_text='An associated INSDC GenBank accession number.', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='sequences',
            name='seqData_projectNumber',
            field=models.CharField(blank=True, help_text='An associated INSDC BioProject number.', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='sequences',
            name='seqData_runNumber',
            field=models.CharField(blank=True, help_text='An associated INSDC run accession number. (ERR number)', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='sequences',
            name='seqData_sampleNumber',
            field=models.CharField(blank=True, help_text='An associated INSDC BioSample number.', max_length=500, null=True),
        ),
    ]
