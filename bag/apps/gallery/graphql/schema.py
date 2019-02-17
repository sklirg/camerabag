import graphene

from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from ..models import Gallery, Image


class ImageNode(DjangoObjectType):
    image_url = graphene.String()

    class Meta:
        model = Image
        filter_fields = ['title', 'datetime']
        interfaces = (relay.Node,)

    def resolve_image_url(self, info):
        server_path = f"{info.context.scheme}://{info.context.get_host()}{self.image_url}"
        return server_path


class GalleryNode(DjangoObjectType):
    class Meta:
        model = Gallery
        filter_fields = ['title']
        interfaces = (relay.Node,)


class Query(object):
    image = relay.Node.Field(ImageNode)
    all_images = DjangoFilterConnectionField(ImageNode)

    gallery = relay.Node.Field(GalleryNode)
    all_galleries = DjangoFilterConnectionField(GalleryNode)
