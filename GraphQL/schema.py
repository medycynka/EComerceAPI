import graphene
from graphene_django.debug import DjangoDebug

from API.schema import schema as api_schema


class APIQuery(api_schema.query, graphene.ObjectType):
    # debug option
    debug = graphene.Field(DjangoDebug, name='_debug')


schema = graphene.Schema(query=APIQuery)
