# Generated by Django 2.1.7 on 2019-02-21 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0007_auto_20190219_0109'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='thumbnail_file',
            field=models.FileField(default='', max_length=1000, upload_to=''),
            preserve_default=False,
        ),
    ]
