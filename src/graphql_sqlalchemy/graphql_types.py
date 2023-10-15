from __future__ import annotations

from graphql import (
    GraphQLBoolean,
    GraphQLFloat,
    GraphQLInputField,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLScalarType,
    GraphQLString,
)
from sqlalchemy import ARRAY, Boolean, Float, Integer
from sqlalchemy.dialects.postgresql import ARRAY as PGARRAY
from sqlalchemy.types import TypeEngine


def get_graphql_type_from_column(column_type: TypeEngine) -> GraphQLScalarType | GraphQLList:
    if isinstance(column_type, Integer):
        return GraphQLInt

    if isinstance(column_type, Float):
        return GraphQLFloat

    if isinstance(column_type, Boolean):
        return GraphQLBoolean

    if isinstance(column_type, (ARRAY, PGARRAY)):
        return GraphQLList(get_graphql_type_from_column(column_type.item_type))

    return GraphQLString


def get_base_comparison_fields(graphql_type: GraphQLScalarType | GraphQLList) -> dict[str, GraphQLInputField]:
    return {
        "_eq": GraphQLInputField(graphql_type),
        "_neq": GraphQLInputField(graphql_type),
        "_in": GraphQLInputField(GraphQLList(GraphQLNonNull(graphql_type))),
        "_nin": GraphQLInputField(GraphQLList(GraphQLNonNull(graphql_type))),
        "_lt": GraphQLInputField(graphql_type),
        "_gt": GraphQLInputField(graphql_type),
        "_gte": GraphQLInputField(graphql_type),
        "_lte": GraphQLInputField(graphql_type),
        "_is_null": GraphQLInputField(GraphQLBoolean),
    }


def get_string_comparison_fields() -> dict[str, GraphQLInputField]:
    return {"_like": GraphQLInputField(GraphQLString), "_nlike": GraphQLInputField(GraphQLString)}
