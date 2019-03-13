import boto3
import os

from datetime import timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from apps.gallery.models import Gallery, Image
from apps.gallery.utils import read_exif_data, get_datetime_from_exif, exif_data_to_python_dict


class Command(BaseCommand):
    help = 'Synchronize images and galleries with S3'

    def add_arguments(self, parser):
        parser.add_argument('-b', '--bucket_name', type=str,
                            help="Bucket name in S3. Uses the configured one by default")
        parser.add_argument('-g', '--gallery_id', type=str,
                            help="ID of a specific gallery")
        parser.add_argument('-m', '--max-keys', type=int,
                            help="Maximum number of keys to fetch")

    def handle(self, *args, **kwargs):
        _bucket_name = kwargs.get('bucket_name', '')
        bucket_name = _bucket_name if _bucket_name else settings.S3_BUCKET_ID
        gallery_id = kwargs.get('gallery_id', '')
        verbosity = kwargs.get('verbosity')
        max_keys = kwargs.get('max_keys', 1000)

        print(f"Syncing bucket '{bucket_name}'")
        list_s3_bucket_objects(
            bucket_name,
            max_keys=max_keys,
            verbosity=verbosity,
        )


def list_s3_bucket_objects(bucket_name, max_keys=1000, verbosity=0):
    objects = []
    last_key = ''
    continuation_token = ''
    counter = 0
    has_more = True

    # Client and request
    client = boto3.client('s3')
    while has_more and counter < 1:
        if continuation_token:
            new_objects = client.list_objects_v2(
                Bucket=bucket_name,
                ContinuationToken=continuation_token,
            )
            continuation_token = ''
        elif last_key:
            new_objects = client.list_objects_v2(
                Bucket=bucket_name,
                StartAfter=last_key,
            )
            last_key = ''
        else:
            response = client.list_objects_v2(
                Bucket=bucket_name, MaxKeys=max_keys)

        # USE IS TRUNCATED
        has_more = response.get('IsTruncated', False)
        new_objects = response.get('Contents', [])
        last_key = new_objects[-1].get('Key', '')
        continuation_token = response.get('NextContinuationToken', '')
        print(f"Fetched {len(new_objects)} items. " +
              f"Asked to retry after '{last_key}' with '{continuation_token}' ")

        objects.extend(new_objects)
        counter += 1

    print(f"Ran for {counter} iterations, " +
          f"fetched a total of {len(objects)} objects.")

    galleries = []
    images = []
    allowed_image_file_endings = ['jpg']

    for obj in objects:
        key = obj.get('Key')
        (gallery, image) = key.split('/')

        if gallery not in galleries:
            galleries.append(gallery)

        if not (gallery and image):
            # This might be only a gallery folder, not an image
            continue

        file_ending = image.split('.')[-1].lower()
        if file_ending not in allowed_image_file_endings:
            print(f"{image} does not have allowed file ending {file_ending}. " +
                  "Skipping.")
            continue

        if '_thumb' in key:
            print(f"Skipping thumb files.")
            continue

        # All checks passed, this is an image.
        images.append((key, gallery, image))

    for gallery in galleries:
        try:
            g = Gallery.objects.get(id=gallery)
            print(f"Found existing gallery '{g.title}' for '{gallery}'")
        except Gallery.DoesNotExist:
            Gallery.objects.create(
                id=gallery,
                title=gallery,
                slug=slugify(gallery),
                public=False,
            )
            print(f"Created missing gallery for '{gallery}'")

    only_images = [i[2] for i in images]
    existing_images = \
        [i.title for i in Image.objects.filter(title__in=only_images)]
    print(f"Found {len(existing_images)} existing images " +
          f"in the set of {len(only_images)} images")

    images_to_create = []
    skipped = 0
    for i in images:
        (key, gallery, image) = i
        if image in existing_images:
            if verbosity >= 2:
                print("Image in existing images.. skipping")
            continue
        image_url = f"{settings.MEDIA_URL}{gallery}/{image}"
        images_to_create.append(Image(
            gallery_id=gallery,
            title=image,
            image_url=image_url,
            datetime=timezone.now(),  # ToDo: Get from exif data
            public=False,
        ))
        if verbosity >= 2:
            print("Adding new image")

    print(f"Creating {len(images_to_create)} images")

    created_images = Image.objects.bulk_create(images_to_create)

    print(f"Done creating {len(created_images)} images")

    update_metadata_objects([i[0] for i in images],
                            bucket_name, verbosity=verbosity)


def update_metadata_objects(image_keys, bucket, verbosity=0):
    # Get images that are recently added and update them with exif data
    probably_fresh_images_timestamp = timezone.now() - timedelta(minutes=30)
    fresh_images = Image.objects.filter(
        datetime__gte=probably_fresh_images_timestamp)
    image_ids = [i.title for i in fresh_images]
    image_gallery_ids = [f"{i.gallery.id}/{i.title}" for i in fresh_images]

    print(f"Found {len(fresh_images)} recently added images. " +
          "Fetching images to update metadata.")

    objects_to_update = []
    for key in image_keys:
        for image_id in image_ids:
            if image_id in key:
                objects_to_update.append(key)

    print(f"Found cached s3 objects for " +
          f"{len(objects_to_update)}/{len(image_keys)} objects")

    for obj in objects_to_update:
        update_metadata(obj, bucket, verbosity=verbosity)


def update_metadata(key, bucket, verbosity=0):
    client = boto3.client('s3')

    print(f"Updating metadata for {key}")

    (gallery, image) = key.split('/')
    if not (gallery and image):
        print(f"Missing gallery ({gallery}) or image ({image})!")
        return

    try:
        image_to_update = Image.objects.get(gallery_id=gallery, title=image)
    except Image.DoesNotExist:
        print(f"Image '{image}' in gallery '{gallery}' does not exist.")
        return

    path = f'/tmp/{gallery}-{image}'

    with open(path, 'wb') as f:
        if verbosity >= 2:
            print(f"Downloading '{key}' to update metadata...")
        client.download_fileobj(bucket, key, f)

    if verbosity >= 2:
        print(f"Reading exif data")
    exif_data = read_exif_data(path)

    if verbosity >= 2:
        print(f"Deleting downloaded file")
    os.remove(path)

    image_datetime = get_datetime_from_exif(exif_data['EXIF DateTimeOriginal'])
    exif_python_data = exif_data_to_python_dict(exif_data)

    if verbosity >= 2:
        print(f"Image datetime: {image_datetime} " +
              f"(from: {exif_data['EXIF DateTimeOriginal']})")

    image_to_update.datetime = image_datetime
    image_to_update.exif_data = exif_python_data
    image_to_update.save()

    print(f"Updated {key} successfully")
