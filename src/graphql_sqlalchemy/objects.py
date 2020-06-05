from typing import Dict

from sqlalchemy import Column
from sqlalchemy.orm import interfaces
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLList,
    GraphQLInputObjectType,
    GraphQLString,
)

from .resolvers import make_field_resolver
from .scalars import get_graphql_type_from_column, get_base_comparison_fields, get_string_comparison_fields
from .names import get_table_name, get_scalar_comparison_name


def build_table_type(model: DeclarativeMeta, objects: Dict[str, GraphQLObjectType]) -> GraphQLObjectType:
    table = model.__table__  # type: ignore

    def get_fields():
        fields = {}

        for column in table.columns:
            graphql_type = get_graphql_type_from_column(column)
            fields[column.name] = GraphQLField(graphql_type, resolve=make_field_resolver(column.name))

        for name, relationship in model.__mapper__.relationships.items():
            object_type = objects[get_table_name(relationship.mapper.entity)]
            if relationship.direction in (interfaces.ONETOMANY, interfaces.MANYTOMANY):
                object_type = GraphQLList(object_type)

            fields[name] = fields[name] = GraphQLField(object_type, resolve=make_field_resolver(name),)

        return fields

    return GraphQLObjectType(get_table_name(model), get_fields)


def get_comparison_object_type(column: Column, inputs: Dict[str, GraphQLInputObjectType]) -> GraphQLInputObjectType:
    scalar = get_graphql_type_from_column(column)
    type_name = get_scalar_comparison_name(scalar)

    if type_name in inputs:
        return inputs[type_name]

    fields = get_base_comparison_fields(scalar)

    if scalar == GraphQLString:
        fields.update(get_string_comparison_fields())

    object_type = GraphQLInputObjectType(type_name, fields)
    inputs[type_name] = object_type

    return object_type
