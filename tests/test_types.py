from __future__ import annotations

from graphql import GraphQLInt
from graphql_sqlalchemy.graphql_types import get_graphql_type_from_column
from sqlalchemy import Column, Integer


def describe_get_graphql_type_from_column() -> None:
    def handles_int() -> None:
        column = Column("name", Integer)

        assert get_graphql_type_from_column(column.type) == GraphQLInt
