from typing import Optional, Dict

from graphql import (
    GraphQLArgument,
    GraphQLNonNull,
    GraphQLList,
    GraphQLInt,
)
from sqlalchemy.ext.declarative import DeclarativeMeta

from .scalars import get_graphql_type_from_column
from .inputs import make_where_type, make_order_type, make_insert_type
from .types import Inputs


PAGINATION_ARGS = {"limit": GraphQLInt, "offset": GraphQLInt}


def make_args(model: DeclarativeMeta, inputs: Inputs) -> Dict[str, GraphQLArgument]:
    args = {}
    for name, field in PAGINATION_ARGS.items():
        args[name] = GraphQLArgument(field)

    order_type = make_order_type(model, inputs)
    args["order"] = GraphQLArgument(GraphQLList(GraphQLNonNull(order_type)))

    where_type = make_where_type(model, inputs)
    args["where"] = GraphQLArgument(where_type)

    return args


def make_pk_args(model: DeclarativeMeta) -> Optional[Dict[str, GraphQLArgument]]:
    primary_key = model.__table__.primary_key  # type: ignore

    if not primary_key:
        return None

    args = {}
    for column in primary_key.columns:
        graphql_type = get_graphql_type_from_column(column)
        args[column.name] = GraphQLArgument(GraphQLNonNull(graphql_type))

    return args


def make_insert_args(model: DeclarativeMeta) -> Dict[str, GraphQLArgument]:
    return {"objects": GraphQLArgument(GraphQLNonNull(GraphQLList(GraphQLNonNull(make_insert_type(model)))))}
