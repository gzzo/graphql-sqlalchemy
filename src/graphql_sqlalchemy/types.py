from sqlalchemy import Integer, Float, Boolean
from graphql import GraphQLString, GraphQLInt, GraphQLFloat, GraphQLBoolean


def get_graphql_type_from_column(column):
    if isinstance(column.type, Integer):
        return GraphQLInt

    if isinstance(column.type, Float):
        return GraphQLFloat

    if isinstance(column.type, Boolean):
        return GraphQLBoolean

    return GraphQLString
