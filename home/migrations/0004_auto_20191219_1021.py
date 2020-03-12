# Generated by Django 2.2.5 on 2019-12-19 10:21

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import taggit.managers
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('home', '0003_auto_20191103_1140'),
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('html', wagtail.core.fields.StreamField([('insert_html', wagtail.core.blocks.RawHTMLBlock(help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element', required=False))], blank=True)),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('card', models.ManyToManyField(to='home.Card')),
            ],
        ),
        migrations.CreateModel(
            name='SectionPlacement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='section_placements', to='home.HomePage')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Section')),
            ],
            options={
                'verbose_name': 'section placement',
                'verbose_name_plural': 'section placements',
            },
        ),
        migrations.CreateModel(
            name='CardTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='tagged_items', to='home.Card')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_cardtag_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='card',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='home.CardTag', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]