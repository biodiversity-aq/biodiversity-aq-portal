# Generated by Django 2.2.5 on 2020-02-26 14:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailforms', '0003_capitalizeverbose'),
        ('wagtailredirects', '0006_redirect_increase_max_length'),
        ('wagtailmenus', '0023_remove_use_specific'),
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
        ('home', '0019_auto_20200224_1317'),
    ]

    operations = [
        migrations.CreateModel(
            name='DetailIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.RemoveField(
            model_name='threecolumnpage',
            name='page_ptr',
        ),
        migrations.RemoveField(
            model_name='twocolumnpage',
            name='page_ptr',
        ),
        migrations.DeleteModel(
            name='OneColumnPage',
        ),
        migrations.DeleteModel(
            name='ThreeColumnPage',
        ),
        migrations.DeleteModel(
            name='TwoColumnPage',
        ),
    ]