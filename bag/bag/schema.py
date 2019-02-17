import graphene

from apps.gallery.graphql import schema as gallery_schema


class Query(gallery_schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
