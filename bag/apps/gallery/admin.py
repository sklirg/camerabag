from django.contrib import admin

from .models import Gallery, Image
from .management.commands.s3_gallery_sync import Command as SyncCommand


def make_public(modeladmin, request, queryset):
    queryset.update(public=True)


def make_not_public(modeladmin, request, queryset):
    queryset.update(public=False)


def sync_galleries_with_s3(modeladmin, request, queryset):
    cmd = SyncCommand()
    for gallery in queryset.all():
        cmd.handle(gallery_id=gallery.id)


def force_sync_galleries_with_s3(modeladmin, request, queryset):
    cmd = SyncCommand()
    for gallery in queryset.all():
        cmd.handle(gallery_id=gallery.id, force=True)


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ['title', 'public', 'number_of_images']
    list_filter = ['public']
    search_fields = ['title']
    actions = [make_public, make_not_public,
               sync_galleries_with_s3, force_sync_galleries_with_s3]

    def number_of_images(self, obj):
        return obj.image_set.count()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj=obj, **kwargs)
        if not obj:
            return form

        form.base_fields["thumbnail_image"].queryset = Image.objects.filter(
            gallery__id=obj.id)

        return form


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'gallery', 'public', 'datetime', 'image_url']
    list_filter = ['public', 'gallery', 'datetime']
    search_fields = ['title', 'gallery__title']
    actions = [make_public, make_not_public]
