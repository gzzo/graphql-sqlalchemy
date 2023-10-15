from __future__ import annotations

from graphql import (
    GraphQLField,
    GraphQLFieldMap,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLOutputType,
)
from sqlalchemy.orm import DeclarativeBase, interfaces

from .graphql_types import get_graphql_type_from_column
from .helpers import get_relationships, get_table
from .names import get_field_name, get_table_name
from .resolvers import make_field_resolver
from .types import Objects


def build_object_type(model: type[DeclarativeBase], objects: Objects) -> GraphQLObjectType:
    def get_fields() -> GraphQLFieldMap:
        fields = {}

        for column in get_table(model).columns:
            graphql_type: GraphQLOutputType = get_graphql_type_from_column(column.type)
            if not column.nullable:
                graphql_type = GraphQLNonNull(graphql_type)

            fields[column.name] = GraphQLField(graphql_type, resolve=make_field_resolver(column.name))

        for name, relationship in get_relationships(model):
            object_type: GraphQLOutputType = objects[get_table_name(relationship.mapper.entity)]
            if relationship.direction in (interfaces.ONETOMANY, interfaces.MANYTOMANY):
                object_type = GraphQLList(object_type)

            fields[name] = GraphQLField(object_type, resolve=make_field_resolver(name))

        return fields

    return GraphQLObjectType(get_table_name(model), get_fields)


def build_mutation_response_type(model: type[DeclarativeBase], objects: Objects) -> GraphQLObjectType:
    type_name = get_field_name(model, "mutation_response")

    object_type = objects[get_table_name(model)]
    fields = {
        "affected_rows": GraphQLField(GraphQLNonNull(GraphQLInt)),
        "returning": GraphQLField(GraphQLNonNull(GraphQLList(GraphQLNonNull(object_type)))),
    }

    return GraphQLObjectType(type_name, fields)
