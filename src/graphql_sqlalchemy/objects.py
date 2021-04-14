from sqlalchemy import Column
from sqlalchemy.orm import interfaces
from sqlalchemy.ext.declarative import DeclarativeMeta
from graphql import (
    GraphQLField,
    GraphQLFieldMap,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLOutputType,
)

from typing import Any
from .graphql_types import get_graphql_type_from_column
from .helpers import get_relationships, get_table
from .names import get_table_name, get_field_name
from .resolvers import make_field_resolver
from .types import Objects


def build_object_type(model: DeclarativeMeta, objects: Objects) -> GraphQLObjectType:
    def get_column_field(column: Column) -> GraphQLOutputType:
        if column.nullable:
            return get_graphql_type_from_column(column.type)
        else:
            return GraphQLNonNull(get_graphql_type_from_column(column.type))

    def get_relationship_field(relationship: Any) -> GraphQLOutputType:
        if relationship.direction in (interfaces.ONETOMANY, interfaces.MANYTOMANY):
            return GraphQLList(objects[get_table_name(relationship.mapper.entity)])
        else:
            return objects[get_table_name(relationship.mapper.entity)]

    def get_fields() -> GraphQLFieldMap:
        fields = {
            **{column.name: GraphQLField(get_column_field(column), resolve=make_field_resolver(column.name)) for column in get_table(model).columns},
            **{name: GraphQLField(get_relationship_field(relationship), resolve=make_field_resolver(name)) for name, relationship in get_relationships(model)},
        }

        return fields

    return GraphQLObjectType(get_table_name(model), get_fields)


def build_mutation_response_type(model: DeclarativeMeta, objects: Objects) -> GraphQLObjectType:
    type_name = get_field_name(model, "mutation_response")

    object_type = objects[get_table_name(model)]
    fields = {
        "affected_rows": GraphQLField(GraphQLNonNull(GraphQLInt)),
        "returning": GraphQLField(GraphQLNonNull(GraphQLList(GraphQLNonNull(object_type)))),
    }

    return GraphQLObjectType(type_name, fields)
