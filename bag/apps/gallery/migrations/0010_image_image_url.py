# Generated by Django 2.1.7 on 2019-03-13 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0009_auto_20190310_2211'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='image_url',
            field=models.URLField(null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='image_file',
            field=models.FileField(max_length=1000, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='image',
            name='thumbnail_file',
            field=models.FileField(max_length=1000, null=True, upload_to=''),
        ),
    ]
