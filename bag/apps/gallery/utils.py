import json
import os
import pytz

from datetime import datetime
from django.conf import settings
from django.utils import timezone
from exifread import process_file
from zipfile import ZipFile

from .models import Gallery, Image


DEFAULT_TZ = settings.TIME_ZONE

#def get_gallery_duration(gallery: Gallery) -> (datetime, datetime):
    #images = gallery.image_set
    #return now

async def unpack_zip(gallery_id, archive_path):
    unarchive_path = os.path.join(settings.MEDIA_ROOT, gallery_id)

    gallery = Gallery.objects.get(pk=gallery_id)

    with ZipFile(archive_path, 'r') as archive:
        os.makedirs(unarchive_path, exist_ok=True)
        archive.extractall(unarchive_path)

    await create_images_from_files(gallery, unarchive_path, create=True)


async def create_images_from_files(gallery, path, create=True):
    _, __, files = next(os.walk(path))

    image_objects = []

    for file_name in files:
        # Yolo hack
        if "_thumb.jpg" in file_name:
            continue

        image_file_path = f"{gallery.id}/{file_name}"
        exif_data = read_exif_data(os.path.join(path, file_name))

        image_timestamp = timezone.now()
        if exif_data and exif_data.get('EXIF DateTimeOriginal', None):
            image_timestamp = get_datetime_from_exif(exif_data['EXIF DateTimeOriginal'])

        exif_json = exif_data_to_python_dict(exif_data)

        image = Image(
            title=file_name,
            datetime=image_timestamp,
            image_file=image_file_path,
            thumbnail_file=image_file_path.replace(".jpg", "_thumb.jpg"),
            gallery=gallery,
            exif=exif_json,
        )
        image_objects.append(image)

    if create:
        return Image.objects.bulk_create(image_objects)

    return image_objects


def read_exif_data(path):
    data = None
    with open(path, 'rb') as f:
        data = process_file(f)

    return data


def exif_data_to_python_dict(data):
    if not data:
        return {}

    exif_json = {}

    for key in data.keys():
        if key in ['JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote', 'EXIF UserComment']:
            continue

        exif_json[key] = str(data[key])

    return exif_json


def get_datetime_from_exif(exif_datetime, tz_name=DEFAULT_TZ):
    # Example format:
    # 2019:02:07 12:13:01
    dt = datetime.strptime(str(exif_datetime), "%Y:%m:%d %H:%M:%S")
    dt = dt.replace(tzinfo=pytz.timezone(tz_name))
    return dt
