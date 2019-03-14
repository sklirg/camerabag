from django.contrib import admin

from .models import Gallery, Image


def make_public(modeladmin, request, queryset):
    queryset.update(public=True)


def make_not_public(modeladmin, request, queryset):
    queryset.update(public=False)


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ['title', 'public', 'number_of_images']
    list_filter = ['public']
    search_fields = ['title']
    actions = [make_public, make_not_public]

    def number_of_images(self, obj):
        return obj.image_set.count()


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'gallery', 'public', 'datetime', 'image_url']
    list_filter = ['public', 'gallery', 'datetime']
    search_fields = ['title', 'gallery__title']
    actions = [make_public, make_not_public]
