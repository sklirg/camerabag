import graphene

from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from ..models import Gallery, Image


def get_self_uri(request):
    return f"{request.scheme}://{request.get_host()}"


class ImageNode(DjangoObjectType):
    image_url = graphene.String()

    class Meta:
        model = Image
        filter_fields = ['title', 'datetime']
        interfaces = (relay.Node,)

    def resolve_image_url(self, info):
        server_path = f"{get_self_uri(info.context)}{self.image_url}"
        return server_path


class GalleryNode(DjangoObjectType):
    thumbnail = graphene.String()

    class Meta:
        model = Gallery
        filter_fields = ['title']
        interfaces = (relay.Node,)

    def resolve_thumbnail(self, info):
        if self.image_set.count() == 0:
            return self.thumbnail
        return f"{get_self_uri(info.context)}{self.image_set.all()[0].image_url}"


class Query(object):
    image = relay.Node.Field(ImageNode)
    all_images = DjangoFilterConnectionField(ImageNode)

    gallery = relay.Node.Field(GalleryNode)
    all_galleries = DjangoFilterConnectionField(GalleryNode)
