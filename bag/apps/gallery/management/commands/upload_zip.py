import asyncio

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from apps.gallery.models import Gallery
from apps.gallery.utils import unpack_zip

class Command(BaseCommand):
    help = 'Upload zip with images to a gallery'

    def add_arguments(self, parser):
        parser.add_argument('-g', '--gallery_id', type=str, help="The id of the gallery")
        parser.add_argument('zip_path', type=str, help="The path to a zip file to unarchive")

    def handle(self, *args, **kwargs):
        gallery_id = kwargs.get('gallery_id', '')
        zip_path = kwargs.get('zip_path')

        if not gallery_id:
            gallery_name = zip_path.split('/')[-1].split('.')[0]
            gallery = Gallery.objects.create(
                title=gallery_name,
                slug=slugify(gallery_name),
                thumbnail="https://picsum.photos/200?r",
            )
            gallery_id = str(gallery.id)

        asyncio.run(unpack_zip(gallery_id, zip_path))
