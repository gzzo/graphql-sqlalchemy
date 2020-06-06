from sqlalchemy import Column
from sqlalchemy.ext.declarative import DeclarativeMeta
from graphql import (
    GraphQLInputObjectType,
    GraphQLList,
    GraphQLEnumType,
    GraphQLInputField,
    GraphQLString,
    GraphQLInputFieldMap,
    GraphQLNonNull,
)

from .names import (
    get_model_order_by_input_name,
    get_model_where_input_name,
    get_model_insert_input_name,
    get_scalar_comparison_name,
    get_model_conflict_input_name,
    get_model_constraint_enum_name,
    get_model_constraint_key_name,
    get_model_column_update_enum_name,
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

    input_type = GraphQLInputObjectType(type_name, fields)
    inputs[type_name] = input_type
    return input_type


def get_where_type(model: DeclarativeMeta, inputs: Inputs) -> GraphQLInputObjectType:
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

    input_type = GraphQLInputObjectType(type_name, get_fields)
    inputs[type_name] = input_type
    return input_type


def get_order_type(model: DeclarativeMeta, inputs: Inputs) -> GraphQLInputObjectType:
    type_name = get_model_order_by_input_name(model)

    def get_fields() -> GraphQLInputFieldMap:
        fields = {}

        for column in get_table(model).columns:
            fields[column.name] = GraphQLInputField(ORDER_BY_ENUM)

        for name, relationship in get_relationships(model):
            fields[name] = GraphQLInputField(inputs[get_model_order_by_input_name(relationship.mapper.entity)])

        return fields

    input_type = GraphQLInputObjectType(type_name, get_fields)
    inputs[type_name] = input_type
    return input_type


def get_insert_type(model: DeclarativeMeta, inputs: Inputs) -> GraphQLInputObjectType:
    type_name = get_model_insert_input_name(model)
    if type_name in inputs:
        return inputs[type_name]

    fields = {}
    for column in get_table(model).columns:
        fields[column.name] = GraphQLInputField(get_graphql_type_from_column(column))

    input_type = GraphQLInputObjectType(type_name, fields)
    inputs[type_name] = input_type
    return input_type


def get_constraint_enum(model: DeclarativeMeta) -> GraphQLEnumType:
    type_name = get_model_constraint_enum_name(model)

    fields = {}
    for column in get_table(model).primary_key:
        key_name = get_model_constraint_key_name(model, column, is_primary_key=True)
        fields[key_name] = key_name

    return GraphQLEnumType(type_name, fields)


def get_update_column_enums(model: DeclarativeMeta) -> GraphQLEnumType:
    type_name = get_model_column_update_enum_name(model)

    fields = {}
    for column in get_table(model).columns:
        fields[column.name] = column.name

    return GraphQLEnumType(type_name, fields)


def get_conflict_type(model: DeclarativeMeta, inputs: Inputs) -> GraphQLInputObjectType:
    type_name = get_model_conflict_input_name(model)
    if type_name in inputs:
        return inputs[type_name]

    fields = {
        "constraint": GraphQLInputField(GraphQLNonNull(get_constraint_enum(model))),
        "update_columns": GraphQLInputField(
            GraphQLNonNull(GraphQLList(GraphQLNonNull(get_update_column_enums(model))))
        ),
        "where": GraphQLInputField(get_where_type(model, inputs)),
    }

    input_type = GraphQLInputObjectType(type_name, fields)
    inputs[type_name] = input_type
    return input_type
