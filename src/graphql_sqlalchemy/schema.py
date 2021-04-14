from graphql import GraphQLField, GraphQLFieldMap, GraphQLList, GraphQLNonNull, GraphQLObjectType, GraphQLSchema
from sqlalchemy.ext.declarative import DeclarativeMeta

from .args import (
    make_query_args,
    make_pk_args,
    make_mutation_args,
)
from .helpers import get_pk_columns
from .names import (
    get_table_name,
    get_field_name,
)
from .objects import build_mutation_response_type, build_object_type
from .resolvers import (
    make_query_resolver,
    make_pk_resolver,
    make_insert_one_resolver,
    make_insert_resolver,
    make_update_by_pk_resolver,
    make_update_resolver,
    make_delete_by_pk_resolver,
    make_delete_resolver,
)
from .types import Inputs, Objects


def build_schema(base: DeclarativeMeta, enable_subscription: bool = False) -> GraphQLSchema:
    """

    Args:
      base:
      enable_subscription:

    Returns: :class:`graphql:graphql.type.GraphQLSchema`

    """

    queries: GraphQLFieldMap = {}
    mutations: GraphQLFieldMap = {}

    objects: Objects = {}
    inputs: Inputs = {}

    for model in base.__subclasses__():
        build_queries(model, objects, queries, inputs)
        build_mutations(model, objects, mutations, inputs)

    return GraphQLSchema(
        GraphQLObjectType("Query", queries),
        GraphQLObjectType("Mutation", mutations),
        GraphQLObjectType("Subscription", {}) if enable_subscription else None,
    )


def build_queries(model: DeclarativeMeta, objects: Objects, queries: GraphQLFieldMap, inputs: Inputs) -> None:
    object_type = build_object_type(model, objects)
    objects[object_type.name] = object_type

    queries[object_type.name] = GraphQLField(
        GraphQLNonNull(GraphQLList(GraphQLNonNull(object_type))),
        args=make_query_args(model, inputs=inputs),
        resolve=make_query_resolver(model),
    )

    if get_pk_columns(model):
        queries[get_field_name(model, "by_pk")] = GraphQLField(object_type, args=make_pk_args(model), resolve=make_pk_resolver(model))


def build_mutations(model: DeclarativeMeta, objects: Objects, mutations: GraphQLFieldMap, inputs: Inputs) -> None:
    mutation_response_type = build_mutation_response_type(model, objects)
    object_type = objects[get_table_name(model)]

    resolvers = {
        "insert": [make_insert_resolver(model), mutation_response_type],
        "insert_one": [make_insert_one_resolver(model), object_type],
        "update": [make_update_resolver(model), mutation_response_type],
        **({"update_by_pk": [make_update_by_pk_resolver(model), object_type]} if get_pk_columns(model) else {}),
        "delete": [make_delete_resolver(model), mutation_response_type],
        **({"delete_by_pk": [make_delete_by_pk_resolver(model), object_type]} if get_pk_columns(model) else {}),
    }

    for mutation_name in resolvers.keys():
        mutations[get_field_name(model, mutation_name)] = GraphQLField(resolvers[mutation_name][1], args=make_mutation_args(model, inputs, mutation_name), resolve=resolvers[mutation_name][0])  # type: ignore
