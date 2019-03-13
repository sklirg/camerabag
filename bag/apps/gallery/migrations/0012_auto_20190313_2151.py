# Generated by Django 2.1.7 on 2019-03-13 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0011_auto_20190313_2140'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='image',
            options={'ordering': ['datetime', 'title', 'image_url']},
        ),
        migrations.AlterField(
            model_name='image',
            name='image_url',
            field=models.URLField(),
        ),
        migrations.RemoveField(
            model_name='image',
            name='image_file',
        ),
        migrations.RemoveField(
            model_name='image',
            name='thumbnail_file',
        ),
    ]