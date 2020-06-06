from sqlalchemy import Column, Integer, Float
from sqlalchemy.ext.declarative import DeclarativeMeta
from graphql import (
    GraphQLInputObjectType,
    GraphQLList,
    GraphQLEnumType,
    GraphQLInputField,
    GraphQLString,
    GraphQLInputFieldMap,
    GraphQLNonNull,
    GraphQLBoolean,
)

from .names import (
    get_model_order_by_input_name,
    get_model_where_input_name,
    get_model_insert_input_name,
    get_scalar_comparison_name,
    get_model_conflict_input_name,
    get_model_inc_input_type_name,
    get_model_set_input_type_name,
    get_model_pk_columns_input_type_name,
)
from .scalars import get_graphql_type_from_column, get_base_comparison_fields, get_string_comparison_fields
from .types import Inputs
from .helpers import get_table, get_relationships


ORDER_BY_ENUM = GraphQLEnumType("order_by", {"desc": "desc", "asc": "asc"})


def get_comparison_input_type(column: Column, inputs: Inputs) -> GraphQLInputObjectType:
    scalar = get_graphql_type_from_column(column)
    type_name = get_scalar_comparison_name(scalar)

    if type_name in inputs:
        return inputs[type_name]

    fields = get_base_comparison_fields(scalar)

    if scalar == GraphQLString:
        fields.update(get_string_comparison_fields())

    inputs[type_name] = GraphQLInputObjectType(type_name, fields)
    return inputs[type_name]


def get_where_input_type(model: DeclarativeMeta, inputs: Inputs) -> GraphQLInputObjectType:
    type_name = get_model_where_input_name(model)
    if type_name in inputs:
        return inputs[type_name]

    def get_fields() -> GraphQLInputFieldMap:
        fields = {
            "_and": GraphQLInputField(GraphQLList(inputs[type_name])),
            "_or": GraphQLInputField(GraphQLList(inputs[type_name])),
            "_not": GraphQLInputField(inputs[type_name]),
        }

        for column in get_table(model).columns:
            fields[column.name] = GraphQLInputField(get_comparison_input_type(column, inputs))

        for name, relationship in get_relationships(model):
            fields[name] = GraphQLInputField(inputs[get_model_where_input_name(relationship.mapper.entity)])

        return fields

    inputs[type_name] = GraphQLInputObjectType(type_name, get_fields)
    return inputs[type_name]


def get_order_input_type(model: DeclarativeMeta, inputs: Inputs) -> GraphQLInputObjectType:
    type_name = get_model_order_by_input_name(model)

    def get_fields() -> GraphQLInputFieldMap:
        fields = {}

        for column in get_table(model).columns:
            fields[column.name] = GraphQLInputField(ORDER_BY_ENUM)

        for name, relationship in get_relationships(model):
            fields[name] = GraphQLInputField(inputs[get_model_order_by_input_name(relationship.mapper.entity)])

        return fields

    inputs[type_name] = GraphQLInputObjectType(type_name, get_fields)
    return inputs[type_name]


def make_model_fields_input_type(model: DeclarativeMeta, type_name: str) -> GraphQLInputObjectType:
    fields = {}
    for column in get_table(model).columns:
        fields[column.name] = GraphQLInputField(get_graphql_type_from_column(column))

    return GraphQLInputObjectType(type_name, fields)


def get_insert_input_type(model: DeclarativeMeta, inputs: Inputs) -> GraphQLInputObjectType:
    type_name = get_model_insert_input_name(model)
    if type_name in inputs:
        return inputs[type_name]

    inputs[type_name] = make_model_fields_input_type(model, type_name)
    return inputs[type_name]


def get_conflict_input_type(model: DeclarativeMeta, inputs: Inputs) -> GraphQLInputObjectType:
    type_name = get_model_conflict_input_name(model)
    if type_name in inputs:
        return inputs[type_name]

    fields = {
        "merge": GraphQLInputField(GraphQLNonNull(GraphQLBoolean)),
    }

    input_type = GraphQLInputObjectType(type_name, fields)
    inputs[type_name] = input_type
    return input_type


def get_inc_input_type(model: DeclarativeMeta, inputs: Inputs) -> GraphQLInputObjectType:
    type_name = get_model_inc_input_type_name(model)
    if type_name in inputs:
        return inputs[type_name]

    fields = {}
    for column in get_table(model).columns:
        if isinstance(column.type, (Integer, Float)):
            fields[column.name] = GraphQLInputField(get_graphql_type_from_column(column))

    inputs[type_name] = GraphQLInputObjectType(type_name, fields)
    return inputs[type_name]


def get_set_input_type(model: DeclarativeMeta, inputs: Inputs) -> GraphQLInputObjectType:
    type_name = get_model_set_input_type_name(model)
    if type_name in inputs:
        return inputs[type_name]

    inputs[type_name] = make_model_fields_input_type(model, type_name)
    return inputs[type_name]


def get_pk_columns_input(model: DeclarativeMeta) -> GraphQLInputObjectType:
    type_name = get_model_pk_columns_input_type_name(model)
    primary_key = get_table(model).primary_key

    fields = {}
    for column in primary_key.columns:
        fields[column.name] = GraphQLInputField(GraphQLNonNull(get_graphql_type_from_column(column)))

    return GraphQLInputObjectType(type_name, fields)
