from typing import Dict

from sqlalchemy.ext.declarative.api import DeclarativeMeta
from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLSchema,
    GraphQLList,
    GraphQLInputObjectType,
)

from .resolvers import make_resolver, make_pk_resolver
from .inputs import make_args, make_pk_args
from .names import get_model_pk_field_name
from .objects import build_table_type


def build_schema(base: DeclarativeMeta) -> GraphQLSchema:
    fields: Dict[str, GraphQLField] = {}
    objects: Dict[str, GraphQLObjectType] = {}
    inputs: Dict[str, GraphQLInputObjectType] = {}

    for model in base.__subclasses__():
        object_type = build_table_type(model, objects)

        objects[object_type.name] = object_type
        fields[object_type.name] = GraphQLField(
            GraphQLList(object_type), args=make_args(model, inputs=inputs), resolve=make_resolver(model)
        )

        pk_field_name = get_model_pk_field_name(model)
        fields[pk_field_name] = GraphQLField(object_type, args=make_pk_args(model), resolve=make_pk_resolver(model))

    return GraphQLSchema(GraphQLObjectType("Query", fields))
