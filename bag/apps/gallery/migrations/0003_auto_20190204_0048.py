# Generated by Django 2.1.5 on 2019-02-04 00:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0002_auto_20190204_0047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gallery',
            name='thumbnail',
            field=models.URLField(default=''),
            preserve_default=False,
        ),
    ]
