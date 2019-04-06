import uuid

from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField


class Gallery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField()
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    thumbnail = models.URLField(blank=True, null=True)
    thumbnail_image = models.ForeignKey(
        "Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    public = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_thumbnail_url(self):
        if self.thumbnail_image:
            return self.thumbnail_image.image_url

        if self.thumbnail:
            return self.thumbnail

        if self.image_set.count() == 0:
            return self.thumbnail

        return self.image_set.first().image_url

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

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['datetime', 'title', 'image_url']
