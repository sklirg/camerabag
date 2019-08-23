import boto3
import os

from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify

from celery import shared_task

from .models import Gallery, Image
from .utils import exif_data_to_python_dict, get_datetime_from_exif, read_exif_data
from .validators import validate_image_sizes_json


@shared_task()
def sync_s3_bucket(bucket_name, force=False, gallery_id='', max_keys=1000, verbosity=0):
    objects = []
    last_key = ''
    continuation_token = ''
    counter = 0
    has_more = True
    kwargs = {
        'Bucket': bucket_name,
        'MaxKeys': max_keys,
        'Prefix': str(gallery_id),
    }

    # Client and request
    client = boto3.client('s3', aws_access_key_id=settings.S3_AWS_ACCESS_KEY,
                          aws_secret_access_key=settings.S3_AWS_SECRET_KEY)
    while has_more and counter < 10:
        response = client.list_objects_v2(**kwargs)

        # USE IS TRUNCATED
        has_more = response.get('IsTruncated', False)
        new_objects = response.get('Contents', [])
        last_key = '' if len(
            new_objects) == 0 else new_objects[-1].get('Key', '')
        total_keys = response.get('KeyCount')

        continuation_token = response.get('NextContinuationToken', '')
        print(f"Fetched {len(new_objects)} items. Total: {total_keys}")
        if has_more:
            print(f"Asked to retry after '{last_key}' " +
                  f"with '{continuation_token}' ")
            kwargs['ContinuationToken'] = continuation_token

        objects.extend(new_objects)
        counter += 1

    print(f"Ran for {counter} iterations, " +
          f"fetched a total of {len(objects)} objects.")

    galleries = []
    images = []
    allowed_image_file_endings = ['jpg']
    image_sizes = {}

    for obj in objects:
        key = obj.get('Key')
        components = key.split('/')
        if len(components) != 2:
            print(f"Skipping object {key}")
            continue

        (gallery, image) = components

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

        if '_' in key:
            (*start, ending) = image.split("_")
            raw_image = start[0]
            size = ending.split(".")[0]

            raw_image = f"{raw_image}.jpg"
            if raw_image not in image_sizes:
                image_sizes[raw_image] = []

            absolute_image_url = create_image_url(gallery, image)
            image_srcset_size_formatted = f"{absolute_image_url} {size}"

            if verbosity >= 2:
                print(
                    f"Adding image size '{image_srcset_size_formatted}' for image {image} (key source: {key}) (url: {absolute_image_url})")

            try:
                validate_image_sizes_json([image_srcset_size_formatted])
                image_sizes[raw_image].append(image_srcset_size_formatted)
            except ValidationError as e:
                print(
                    f"Image source invalid '{image}' failed validation. Error: {e}")
                continue

            image = raw_image

        # All checks passed, this is an image.
        if image not in [image[2] for image in images]:
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
                print("Image in existing images.. updating some metadata...")

            image_to_update = Image.objects.get(title=image)
            should_update = False

            if image in image_sizes and image_to_update.sizes != image_sizes:
                print(f"Updating {image} with image sizes")
                image_to_update.sizes = image_sizes[image]
                should_update = True

            if should_update:
                try:
                    image_to_update.save()
                except ValidationError as e:
                    print(
                        f"Saving updated image '{image}' failed validation. Error: {e}")
            continue
        image_url = create_image_url(gallery, image)
        images_to_create.append(Image(
            gallery_id=gallery,
            title=image,
            image_url=image_url,
            datetime=timezone.now(),  # ToDo: Get from exif data
            public=False,
            sizes=image_sizes[image] if image in image_sizes else []
        ))
        if verbosity >= 2:
            num_sizes = 0 if image not in image_sizes else image_sizes[image]
            print(f"Adding new image with {num_sizes} sizes")

    print(f"Creating {len(images_to_create)} images")

    created_images = Image.objects.bulk_create(images_to_create)

    print(f"Done creating {len(created_images)} images")

    update_metadata_objects([i[0] for i in images],
                            bucket_name, force=force, verbosity=verbosity)


def update_metadata_objects(image_keys, bucket, force=False, verbosity=0):
    if force:
        print("Running force-update")
    # Get images that are recently added and update them with exif data
    gallery_id = image_keys[0].split("/")[0]
    probably_fresh_images_timestamp = timezone.now() - timedelta(minutes=30)
    fresh_images = Image.objects.filter(
        datetime__gte=probably_fresh_images_timestamp) if not force else Image.objects.filter(gallery__id=gallery_id)
    image_ids = [i.title for i in fresh_images]
    image_gallery_ids = [f"{i.gallery.id}/{i.title}" for i in fresh_images]

    print(f"Updating {len(fresh_images)} images." +
          "Fetching images to update metadata.")

    objects_to_update = []
    for key in image_keys:
        for image_id in image_ids:
            if image_id in key:
                objects_to_update.append(key)

    print(f"Found cached s3 objects for " +
          f"{len(objects_to_update)}/{len(image_keys)} objects")

    counter = 0
    poke_every = min(50, max(1, len(objects_to_update) // 100))

    print(f"Starting metadata update for {len(objects_to_update)} items. " +
          f"Updating every {poke_every} updates.")
    for obj in objects_to_update:
        if counter % poke_every == 0:
            print(f"{counter}/{len(objects_to_update)}")
        update_metadata(obj, bucket, force=force, verbosity=verbosity)
        counter += 1


def update_metadata(key, bucket, force=False, verbosity=0):
    client = boto3.client('s3', aws_access_key_id=settings.S3_AWS_ACCESS_KEY,
                          aws_secret_access_key=settings.S3_AWS_SECRET_KEY)

    if verbosity >= 2:
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

    if verbosity >= 2:
        print(f"Image datetime: {image_datetime} " +
              f"(from: {exif_data['EXIF DateTimeOriginal']})")

    image_to_update.datetime = image_datetime
    image_to_update.exif = exif_data_to_python_dict(exif_data)
    image_to_update.save()

    if verbosity >= 2:
        print(f"Updated {key} successfully")


def create_image_url(gallery, image):
    return f"{settings.MEDIA_URL}{gallery}/{image}"
