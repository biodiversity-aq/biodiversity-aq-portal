# Generated by Django 2.2.12 on 2020-04-20 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0034_auto_20200416_0726'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detailpage',
            name='show_in_parent',
        ),
        migrations.RemoveField(
            model_name='overviewpage',
            name='show_in_parent',
        ),
        migrations.RemoveField(
            model_name='redirectdummypage',
            name='show_in_parent',
        ),
        migrations.AddField(
            model_name='detailpage',
            name='show_in_recent',
            field=models.BooleanField(blank=True, default=False, help_text='If true, this page will appear in the "Recent" section of its parent if it is an AppLandingPage order by last published date', null=True),
        ),
        migrations.AddField(
            model_name='overviewpage',
            name='show_in_recent',
            field=models.BooleanField(blank=True, default=False, help_text='If true, this page will appear in the "Recent" section of its parent if it is an AppLandingPage order by last published date', null=True),
        ),
        migrations.AddField(
            model_name='redirectdummypage',
            name='show_in_recent',
            field=models.BooleanField(blank=True, default=False, help_text='If true, this page will appear in the "Recent" section of its parent if it is an AppLandingPage order by last published date', null=True),
        ),
    ]