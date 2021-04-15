from graphql import GraphQLField, GraphQLFieldMap, GraphQLList, GraphQLNonNull, GraphQLObjectType, GraphQLSchema
from sqlalchemy.ext.declarative import DeclarativeMeta

from .args import (
    make_args,
    make_delete_args,
    make_insert_args,
    make_insert_one_args,
    make_pk_args,
    make_update_args,
    make_update_by_pk_args,
)
from .helpers import get_table
from .names import get_field_name, get_table_name
from .objects import build_mutation_response_type, build_object_type
from .resolvers import (
    make_delete_by_pk_resolver,
    make_delete_resolver,
    make_insert_one_resolver,
    make_insert_resolver,
    make_object_resolver,
    make_pk_resolver,
    make_update_by_pk_resolver,
    make_update_resolver,
)
from .types import Inputs, Objects


def build_queries(model: DeclarativeMeta, objects: Objects, queries: GraphQLFieldMap, inputs: Inputs) -> None:
    object_type = build_object_type(model, objects)

    objects[object_type.name] = object_type
    queries[object_type.name] = GraphQLField(
        GraphQLNonNull(GraphQLList(GraphQLNonNull(object_type))),
        args=make_args(model, inputs=inputs),
        resolve=make_object_resolver(model),
    )

    if get_table(model).primary_key:
        pk_field_name = get_field_name(model, "by_pk")
        queries[pk_field_name] = GraphQLField(object_type, args=make_pk_args(model), resolve=make_pk_resolver(model))


def build_mutations(model: DeclarativeMeta, objects: Objects, mutations: GraphQLFieldMap, inputs: Inputs) -> None:
    mutation_response_type = build_mutation_response_type(model, objects)
    object_type = objects[get_table_name(model)]

    insert_type_name = get_field_name(model, "insert")
    mutations[insert_type_name] = GraphQLField(
        mutation_response_type, args=make_insert_args(model, inputs), resolve=make_insert_resolver(model)
    )

    insert_one_type_name = get_field_name(model, "insert_one")
    mutations[insert_one_type_name] = GraphQLField(
        object_type, args=make_insert_one_args(model, inputs), resolve=make_insert_one_resolver(model)
    )

    delete_type_name = get_field_name(model, "delete")
    mutations[delete_type_name] = GraphQLField(
        mutation_response_type, args=make_delete_args(model, inputs), resolve=make_delete_resolver(model)
    )

    update_type_name = get_field_name(model, "update")
    mutations[update_type_name] = GraphQLField(
        mutation_response_type, args=make_update_args(model, inputs), resolve=make_update_resolver(model)
    )

    if get_table(model).primary_key:
        delete_by_pk_type_name = get_field_name(model, "delete_by_pk")
        mutations[delete_by_pk_type_name] = GraphQLField(
            object_type, args=make_pk_args(model), resolve=make_delete_by_pk_resolver(model)
        )

        update_by_pk_type_name = get_field_name(model, "update_by_pk")
        mutations[update_by_pk_type_name] = GraphQLField(
            object_type, args=make_update_by_pk_args(model, inputs), resolve=make_update_by_pk_resolver(model)
        )


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
