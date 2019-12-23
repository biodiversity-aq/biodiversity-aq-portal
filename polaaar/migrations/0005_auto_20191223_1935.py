# Generated by Django 2.2.5 on 2019-12-23 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polaaar', '0004_auto_20191222_1912'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectmetadata',
            old_name='bounding_box',
            new_name='geom',
        ),
        migrations.AlterField(
            model_name='taxa',
            name='TaxonRank',
            field=models.CharField(blank=True, choices=[('superKingdom', 'superKingdom'), ('Kingdom', 'Kingdom'), ('SubKingdom', 'SubKingdom'), ('Phylum', 'Phylum'), ('SubPhylum', 'SubPhylum'), ('Class', 'Class'), ('SubClass', 'SubClass'), ('Order', 'Order'), ('SubOrder', 'SubOrder'), ('Family', 'Family'), ('SubFamily', 'SubFamily'), ('Genus', 'Genus'), ('SubGenus', 'SubGenus'), ('Species', 'Species'), ('SubSpecies', 'SubSpecies'), ('Strain', 'Strain')], max_length=100, null=True),
        ),
    ]
