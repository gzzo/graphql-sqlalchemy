from typing import Dict

from sqlalchemy.orm import interfaces
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLSchema,
    GraphQLList,
    GraphQLInputObjectType,
)

from .resolvers import make_field_resolver, make_resolver, make_pk_resolver
from .types import get_graphql_type_from_column
from .args import make_args, make_pk_args
from .names import get_model_pk_field_name, get_table_name

Objects = Dict[str, GraphQLObjectType]


def build_table_type(model: DeclarativeMeta, objects: Objects) -> GraphQLObjectType:
    table = model.__table__  # type: ignore

    def get_fields():
        fields = {}

        for column in table.columns:
            graphql_type = get_graphql_type_from_column(column)
            fields[column.name] = GraphQLField(graphql_type, resolve=make_field_resolver(column.name))

        for name, relationship in model.__mapper__.relationships.items():
            object_type = objects[relationship.mapper.entity.__tablename__]
            if relationship.direction in (interfaces.ONETOMANY, interfaces.MANYTOMANY):
                object_type = GraphQLList(object_type)

            fields[name] = fields[name] = GraphQLField(object_type, resolve=make_field_resolver(name),)

        return fields

    return GraphQLObjectType(get_table_name(model), get_fields)


def build_schema(base: DeclarativeMeta) -> GraphQLSchema:
    fields: Dict[str, GraphQLField] = {}
    objects: Dict[str, GraphQLObjectType] = {}
    inputs: Dict[str, GraphQLInputObjectType] = {}

    for model in base.__subclasses__():
        field_name = get_table_name(model)
        object_type = build_table_type(model, objects)

        objects[field_name] = object_type
        fields[field_name] = GraphQLField(
            GraphQLList(object_type), args=make_args(model, inputs=inputs), resolve=make_resolver(model)
        )

        pk_field_name = get_model_pk_field_name(model)
        fields[pk_field_name] = GraphQLField(object_type, args=make_pk_args(model), resolve=make_pk_resolver(model))

    return GraphQLSchema(GraphQLObjectType("Query", fields))
