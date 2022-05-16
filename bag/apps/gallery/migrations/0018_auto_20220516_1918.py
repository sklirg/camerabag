# Generated by Django 3.2 on 2022-05-16 17:18

import apps.gallery.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0017_remove_gallery_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='exif',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='sizes',
            field=models.JSONField(default=list, validators=[apps.gallery.validators.validate_image_sizes_json]),
        ),
    ]