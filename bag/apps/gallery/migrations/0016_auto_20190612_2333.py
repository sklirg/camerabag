# Generated by Django 2.2 on 2019-06-12 21:33

import apps.gallery.validators
import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0015_auto_20190612_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='sizes',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list, validators=[apps.gallery.validators.validate_image_sizes_json]),
        ),
    ]
