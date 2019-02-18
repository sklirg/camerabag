import uuid

from django.conf import settings
from django.db import models


class Gallery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField()
    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    thumbnail = models.URLField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Gallery"
        verbose_name_plural = "Galleries"


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    datetime = models.DateTimeField()
    file = models.FileField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    gallery = models.ForeignKey(Gallery, null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def image_url(self):
        return f"{settings.MEDIA_URL}{self.file}"

    def __str__(self):
        return self.title
