import graphene

from django.conf import settings

from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from ..models import Gallery, Image


def get_self_uri(request):
    return f"{request.scheme}://{request.get_host()}"


class ImageNode(DjangoObjectType):
    class Meta:
        model = Image
        filter_fields = ['title', 'datetime']
        interfaces = (relay.Node,)

    @classmethod
    def get_node(cls, id, info):
        try:
            image = cls._meta.model.objects.get(id=id)
        except cls._meta.model.DoesNotExist:
            return None

        if image.public:
            return image
        return None


class GalleryNode(DjangoObjectType):
    thumbnail = graphene.NonNull(graphene.String)

    class Meta:
        model = Gallery
        filter_fields = ['title']
        interfaces = (relay.Node,)

    @classmethod
    def get_node(cls, id, info):
        try:
            gallery = cls._meta.model.objects.get(id=id)
        except cls._meta.model.DoesNotExist:
            return None

        if gallery.public:
            return gallery
        return None

    def resolve_thumbnail(self, info):
        if self.thumbnail or self.image_set.count() == 0:
            return self.thumbnail

        return self.image_set.first().image_url


class Query(object):
    image = relay.Node.Field(ImageNode)

    all_images = DjangoFilterConnectionField(ImageNode)

    def resolve_all_images(self, info):
        return Image.objects.filter(public=True)

    gallery = relay.Node.Field(GalleryNode)
    all_galleries = DjangoFilterConnectionField(GalleryNode)

    def resolve_all_galleries(self, info):
        return Gallery.objects.filter(public=True)
