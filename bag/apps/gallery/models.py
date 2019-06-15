import uuid

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField

from .validators import validate_image_sizes_json


class Gallery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField()
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    thumbnail_image = models.ForeignKey(
        "Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    public = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def clean(self):
        # Require a thumbnail_image if making gallery public
        if self.public and not self.thumbnail_image:
            raise ValidationError(
                "A gallery requires a thumbnail image if it is to be made public")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.full_clean()
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta:
        verbose_name = "Gallery"
        verbose_name_plural = "Galleries"


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    datetime = models.DateTimeField()
    image_url = models.URLField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    gallery = models.ForeignKey(
        Gallery, null=True, blank=True, on_delete=models.SET_NULL)
    exif = JSONField(blank=True, null=True)
    public = models.BooleanField(default=False)
    # A JSON array of image srcset values, e.g. `image-320w.jpg 320w`
    sizes = JSONField(default=list, validators=[validate_image_sizes_json])

    def __str__(self):
        return self.title

    def clean(self, *args, **kwargs):
        validate_image_sizes_json(self.sizes)
        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['datetime', 'title', 'image_url']
