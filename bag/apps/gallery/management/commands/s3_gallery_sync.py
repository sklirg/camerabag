import boto3
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.gallery.tasks import sync_s3_bucket


class Command(BaseCommand):
    help = 'Synchronize images and galleries with S3'

    def add_arguments(self, parser):
        parser.add_argument('-b', '--bucket_name', type=str,
                            help="Bucket name in S3. Uses the configured one by default")
        parser.add_argument('-g', '--gallery_id', type=str,
                            help="ID of a specific gallery")
        parser.add_argument('-f', '--force', type=bool, default=None,
                            help="ID of a specific gallery")
        parser.add_argument('-m', '--max-keys', type=int,
                            default=1000,
                            help="Maximum number of keys to fetch")
        parser.add_argument('-s', '--synchronous', type=bool,
                            default=False,
                            help="Run synchronously (if set) or defer to async runtime (if not set)")

    def handle(self, *args, **kwargs):
        _bucket_name = kwargs.get('bucket_name', '')
        bucket_name = _bucket_name if _bucket_name else settings.S3_BUCKET_ID
        gallery_id = kwargs.get('gallery_id', '')
        _force = kwargs.get('force')
        force = _force if _force is not None else False
        verbosity = kwargs.get('verbosity', 0)
        max_keys = kwargs.get('max_keys', 1000)
        delay = kwargs.get('synchronous')

        if delay:
            print(f"Syncing bucket '{bucket_name}' asynchronously")
            sync_s3_bucket.delay(
                bucket_name,
                force=force,
                gallery_id=gallery_id,
                max_keys=max_keys,
                verbosity=verbosity,
            )
        else:
            print(f"Syncing bucket '{bucket_name}' synchronously")
            sync_s3_bucket(
                bucket_name,
                force=force,
                gallery_id=gallery_id,
                max_keys=max_keys,
                verbosity=verbosity,
            )
