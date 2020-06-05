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
)


def get_graphql_type_from_column(column: Column) -> GraphQLScalarType:
    if isinstance(column.type, Integer):
        return GraphQLInt

    if isinstance(column.type, Float):
        return GraphQLFloat

    if isinstance(column.type, Boolean):
        return GraphQLBoolean

    return GraphQLString


def get_base_comparison_fields(scalar: GraphQLScalarType) -> Dict[str, GraphQLInputField]:
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


def get_string_comparison_fields() -> Dict[str, GraphQLInputField]:
    return {"_like": GraphQLInputField(GraphQLString), "_nlike": GraphQLInputField(GraphQLString)}
