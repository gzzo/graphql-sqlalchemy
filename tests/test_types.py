from sqlalchemy import Column, Integer
from graphql import GraphQLInt

from graphql_sqlalchemy.scalars import get_graphql_type_from_column


def describe_get_graphql_type_from_column():
    def handles_int():
        column = Column("name", Integer)

        assert get_graphql_type_from_column(column) == GraphQLInt
