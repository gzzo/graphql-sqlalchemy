from graphql import GraphQLArgument, GraphQLArgumentMap, GraphQLInt, GraphQLList, GraphQLNonNull
from sqlalchemy.ext.declarative import DeclarativeMeta

from .graphql_types import get_graphql_type_from_column
from .helpers import has_int, get_pk_columns
from .inputs import get_input_type
from .types import Inputs


PAGINATION_ARGS = {"limit": GraphQLInt, "offset": GraphQLInt}


def make_query_args(model: DeclarativeMeta, inputs: Inputs) -> GraphQLArgumentMap:
    args = {
        "order": GraphQLArgument(GraphQLList(GraphQLNonNull(get_input_type(model, inputs, "order_by")))),
        "where": GraphQLArgument(get_input_type(model, inputs, "where")),
        **PAGINATION_ARGS,  # type: ignore
    }

    return args


def make_pk_args(model: DeclarativeMeta) -> GraphQLArgumentMap:
    pk_columns = get_pk_columns(model)

    return {column.name: GraphQLArgument(GraphQLNonNull(get_graphql_type_from_column(column.type))) for column in pk_columns}


def make_mutation_args(model: DeclarativeMeta, inputs: Inputs, mutation_type: str) -> GraphQLArgumentMap:
    args = {
        "insert": {
            "objects": GraphQLArgument(GraphQLNonNull(GraphQLList(GraphQLNonNull(get_input_type(model, inputs, "insert_input"))))),
            "on_conflict": GraphQLArgument(get_input_type(model, inputs, "on_conflict")),
        },
        "insert_one": {
            "object": GraphQLArgument(get_input_type(model, inputs, "insert_input")),
            "on_conflict": GraphQLArgument(get_input_type(model, inputs, "on_conflict")),
        },
        "update": {
            **({"_inc": GraphQLArgument(get_input_type(model, inputs, "inc_input"))} if has_int(model) else {}),
            "_set": GraphQLArgument(get_input_type(model, inputs, "set_input")),
            "where": GraphQLArgument(get_input_type(model, inputs, "where")),
        },
        "update_by_pk": {
            **({"_inc": GraphQLArgument(get_input_type(model, inputs, "inc_input"))} if has_int(model) else {}),
            "_set": GraphQLArgument(get_input_type(model, inputs, "set_input")),
            **make_pk_args(model),
        },
        "delete": {
            "where": GraphQLArgument(get_input_type(model, inputs, "where")),
        },
        "delete_by_pk": {
            **make_pk_args(model),
        },
    }

    return args[mutation_type]
