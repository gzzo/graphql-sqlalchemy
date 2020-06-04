from typing import Dict

from sqlalchemy import Integer, Float, Boolean, Column
from graphql import (
    GraphQLString,
    GraphQLInt,
    GraphQLFloat,
    GraphQLBoolean,
    GraphQLInputField,
    GraphQLList,
    GraphQLNonNull,
    GraphQLScalarType,
    GraphQLInputObjectType,
)


def get_graphql_type_from_column(column: Column) -> GraphQLScalarType:
    if isinstance(column.type, Integer):
        return GraphQLInt

    if isinstance(column.type, Float):
        return GraphQLFloat

    if isinstance(column.type, Boolean):
        return GraphQLBoolean

    return GraphQLString


def get_base_comparison_fields(scalar: GraphQLScalarType):
    return {
        "_eq": GraphQLInputField(scalar),
        "_neq": GraphQLInputField(scalar),
        "_in": GraphQLInputField(GraphQLList(GraphQLNonNull(scalar))),
        "_nin": GraphQLInputField(GraphQLList(GraphQLNonNull(scalar))),
        "_lt": GraphQLInputField(scalar),
        "_gt": GraphQLInputField(scalar),
        "_gte": GraphQLInputField(scalar),
        "_lte": GraphQLInputField(scalar),
        "_is_null": GraphQLInputField(GraphQLBoolean),
    }


def get_comparison_object_type(column: Column, inputs: Dict[str, GraphQLInputObjectType]) -> GraphQLInputObjectType:
    scalar = get_graphql_type_from_column(column)
    type_name = f"{scalar.name.lower()}_comparison_exp"

    if type_name in inputs:
        return inputs[type_name]

    fields = get_base_comparison_fields(scalar)

    if scalar == GraphQLString:
        fields.update({"_like": GraphQLInputField(GraphQLString), "_nlike": GraphQLInputField(GraphQLString)})

    object_type = GraphQLInputObjectType(type_name, fields)
    inputs[type_name] = object_type

    return object_type
