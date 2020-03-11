# Generated by Django 2.2.5 on 2020-03-09 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polaaar', '0008_homelessfiles'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=1000)),
                ('message', models.CharField(max_length=20000)),
                ('document', models.FileField(upload_to='uploaded/')),
            ],
        ),
    ]
