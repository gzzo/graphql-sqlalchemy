from typing import Union

from graphql import (
    GraphQLBoolean,
    GraphQLFloat,
    GraphQLInt,
    GraphQLList,
    GraphQLScalarType,
    GraphQLString,
)
from sqlalchemy import ARRAY, Boolean, Float, Integer
from sqlalchemy.dialects.postgresql import ARRAY as PGARRAY
from sqlalchemy.types import TypeEngine


def get_graphql_type_from_column(column_type: TypeEngine) -> Union[GraphQLScalarType, GraphQLList]:
    if isinstance(column_type, Integer):
        return GraphQLInt

    if isinstance(column_type, Float):
        return GraphQLFloat

    if isinstance(column_type, Boolean):
        return GraphQLBoolean

    if isinstance(column_type, (ARRAY, PGARRAY)):
        return GraphQLList(get_graphql_type_from_column(column_type.item_type))

    return GraphQLString
