# Generated by Django 2.2 on 2019-06-15 23:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0016_auto_20190612_2333'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gallery',
            name='thumbnail',
        ),
    ]
