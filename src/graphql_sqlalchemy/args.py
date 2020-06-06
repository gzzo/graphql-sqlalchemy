from graphql import (
    GraphQLArgument,
    GraphQLNonNull,
    GraphQLList,
    GraphQLInt,
    GraphQLArgumentMap,
)
from sqlalchemy.ext.declarative import DeclarativeMeta

from .scalars import get_graphql_type_from_column
from .inputs import (
    get_where_input_type,
    get_order_input_type,
    get_insert_input_type,
    get_conflict_input_type,
    get_inc_input_type,
    get_set_input_type,
    get_pk_columns_input,
)
from .types import Inputs
from .helpers import get_table


PAGINATION_ARGS = {"limit": GraphQLInt, "offset": GraphQLInt}


def make_args(model: DeclarativeMeta, inputs: Inputs) -> GraphQLArgumentMap:
    args = {
        "order": GraphQLArgument(GraphQLList(GraphQLNonNull(get_order_input_type(model, inputs)))),
        "where": GraphQLArgument(get_where_input_type(model, inputs)),
    }

    for name, field in PAGINATION_ARGS.items():
        args[name] = GraphQLArgument(field)

    return args


def make_pk_args(model: DeclarativeMeta) -> GraphQLArgumentMap:
    primary_key = get_table(model).primary_key

    args = {}
    for column in primary_key.columns:
        graphql_type = get_graphql_type_from_column(column)
        args[column.name] = GraphQLArgument(GraphQLNonNull(graphql_type))

    return args


def make_insert_args(model: DeclarativeMeta, inputs: Inputs) -> GraphQLArgumentMap:
    return {
        "objects": GraphQLArgument(GraphQLNonNull(GraphQLList(GraphQLNonNull(get_insert_input_type(model, inputs))))),
        "on_conflict": GraphQLArgument(get_conflict_input_type(model, inputs)),
    }


def make_insert_one_args(model: DeclarativeMeta, inputs: Inputs) -> GraphQLArgumentMap:
    return {
        "object": GraphQLArgument(get_insert_input_type(model, inputs)),
        "on_conflict": GraphQLArgument(get_conflict_input_type(model, inputs)),
    }


def make_delete_args(model: DeclarativeMeta, inputs: Inputs) -> GraphQLArgumentMap:
    return {"where": GraphQLArgument(get_where_input_type(model, inputs))}


def make_update_args(model: DeclarativeMeta, inputs: Inputs) -> GraphQLArgumentMap:
    return {
        "_inc": GraphQLArgument(get_inc_input_type(model, inputs)),
        "_set": GraphQLArgument(get_set_input_type(model, inputs)),
        "where": GraphQLArgument(get_where_input_type(model, inputs)),
    }


def make_update_by_pk_args(model: DeclarativeMeta, inputs: Inputs) -> GraphQLArgumentMap:
    return {
        "_inc": GraphQLArgument(get_inc_input_type(model, inputs)),
        "_set": GraphQLArgument(get_set_input_type(model, inputs)),
        "pk_columns": GraphQLArgument(GraphQLNonNull(get_pk_columns_input(model))),
    }
