from graphql import GraphQLInt
from sqlalchemy import Column, Integer

from graphql_sqlalchemy.scalars import get_graphql_type_from_column


def describe_get_graphql_type_from_column() -> None:
    def handles_int() -> None:
        column = Column("name", Integer)

        assert get_graphql_type_from_column(column) == GraphQLInt
