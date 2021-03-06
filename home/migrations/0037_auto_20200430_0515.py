# Generated by Django 2.2.12 on 2020-04-30 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0036_auto_20200427_0516'),
    ]

    operations = [
        migrations.AddField(
            model_name='detailindexpage',
            name='colour_theme',
            field=models.CharField(blank=True, choices=[('#0099CC', 'Default blue'), ('#3952a4', 'Dark blue'), ('#003a4e', 'Dark green'), ('#006f71', 'Teal'), ('#ec6633', 'Orange'), ('#d51e47', 'Red')], default='#0099CC', help_text='Please select a colour theme for the header and footer.', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='detailpage',
            name='colour_theme',
            field=models.CharField(blank=True, choices=[('#0099CC', 'Default blue'), ('#3952a4', 'Dark blue'), ('#003a4e', 'Dark green'), ('#006f71', 'Teal'), ('#ec6633', 'Orange'), ('#d51e47', 'Red')], default='#0099CC', help_text='Please select a colour theme for the header and footer.', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='overviewpage',
            name='colour_theme',
            field=models.CharField(blank=True, choices=[('#0099CC', 'Default blue'), ('#3952a4', 'Dark blue'), ('#003a4e', 'Dark green'), ('#006f71', 'Teal'), ('#ec6633', 'Orange'), ('#d51e47', 'Red')], default='#0099CC', help_text='Please select a colour theme for the header and footer.', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='redirectdummypage',
            name='colour_theme',
            field=models.CharField(blank=True, choices=[('#0099CC', 'Default blue'), ('#3952a4', 'Dark blue'), ('#003a4e', 'Dark green'), ('#006f71', 'Teal'), ('#ec6633', 'Orange'), ('#d51e47', 'Red')], default='#0099CC', help_text='Please select a colour theme for the header and footer.', max_length=200, null=True),
        ),
    ]
