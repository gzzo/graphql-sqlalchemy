from sqlalchemy.ext.declarative.api import DeclarativeMeta
from graphql import GraphQLObjectType, GraphQLField, GraphQLFieldMap, GraphQLSchema, GraphQLList, GraphQLNonNull

from .resolvers import (
    make_object_resolver,
    make_pk_resolver,
    make_insert_resolver,
    make_insert_one_resolver,
    make_delete_resolver,
    make_delete_by_pk_resolver,
    make_update_resolver,
    make_update_by_pk_resolver,
)
from .args import (
    make_args,
    make_pk_args,
    make_insert_args,
    make_insert_one_args,
    make_delete_args,
    make_update_args,
    make_update_by_pk_args,
)
from .names import (
    get_model_pk_field_name,
    get_model_insert_object_name,
    get_model_insert_one_object_name,
    get_table_name,
    get_model_delete_name,
    get_model_delete_by_pk_name,
    get_model_update_name,
    get_model_update_by_pk_name,
)
from .objects import build_object_type, build_mutation_response_type
from .types import Objects, Inputs
from .helpers import get_table


def build_queries(model: DeclarativeMeta, objects: Objects, queries: GraphQLFieldMap, inputs: Inputs) -> None:
    object_type = build_object_type(model, objects)

    objects[object_type.name] = object_type
    queries[object_type.name] = GraphQLField(
        GraphQLNonNull(GraphQLList(GraphQLNonNull(object_type))),
        args=make_args(model, inputs=inputs),
        resolve=make_object_resolver(model),
    )

    if get_table(model).primary_key:
        pk_field_name = get_model_pk_field_name(model)
        queries[pk_field_name] = GraphQLField(object_type, args=make_pk_args(model), resolve=make_pk_resolver(model))


def build_mutations(model: DeclarativeMeta, objects: Objects, mutations: GraphQLFieldMap, inputs: Inputs) -> None:
    mutation_response_type = build_mutation_response_type(model, objects)
    object_type = objects[get_table_name(model)]

    insert_type_name = get_model_insert_object_name(model)
    mutations[insert_type_name] = GraphQLField(
        mutation_response_type, args=make_insert_args(model, inputs), resolve=make_insert_resolver(model)
    )

    insert_one_type_name = get_model_insert_one_object_name(model)
    mutations[insert_one_type_name] = GraphQLField(
        object_type, args=make_insert_one_args(model, inputs), resolve=make_insert_one_resolver(model)
    )

    delete_type_name = get_model_delete_name(model)
    mutations[delete_type_name] = GraphQLField(
        mutation_response_type, args=make_delete_args(model, inputs), resolve=make_delete_resolver(model)
    )

    update_type_name = get_model_update_name(model)
    mutations[update_type_name] = GraphQLField(
        mutation_response_type, args=make_update_args(model, inputs), resolve=make_update_resolver(model)
    )

    if get_table(model).primary_key:
        delete_by_pk_type_name = get_model_delete_by_pk_name(model)
        mutations[delete_by_pk_type_name] = GraphQLField(
            object_type, args=make_pk_args(model), resolve=make_delete_by_pk_resolver(model)
        )

        update_by_pk_type_name = get_model_update_by_pk_name(model)
        mutations[update_by_pk_type_name] = GraphQLField(
            object_type, args=make_update_by_pk_args(model, inputs), resolve=make_update_by_pk_resolver(model)
        )


def build_schema(base: DeclarativeMeta) -> GraphQLSchema:
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
        GraphQLObjectType("Subscription", {}),
    )
