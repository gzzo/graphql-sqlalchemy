from graphql import (
    GraphQLBoolean,
    GraphQLEnumType,
    GraphQLInputField,
    GraphQLInputFieldMap,
    GraphQLInputObjectType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLString,
)
from sqlalchemy import Column, Float, Integer
from sqlalchemy.ext.declarative import DeclarativeMeta

from .graphql_types import get_base_comparison_fields, get_graphql_type_from_column, get_string_comparison_fields
from .helpers import get_relationships, get_table
from .names import (
    get_graphql_type_comparison_name,
    get_model_conflict_input_name,
    get_model_inc_input_type_name,
    get_model_insert_input_name,
    get_model_order_by_input_name,
    get_model_pk_columns_input_type_name,
    get_model_set_input_type_name,
    get_model_where_input_name,
)
from .types import Inputs

ORDER_BY_ENUM = GraphQLEnumType("order_by", {"desc": "desc", "asc": "asc"})


def get_comparison_input_type(column: Column, inputs: Inputs) -> GraphQLInputObjectType:
    graphql_type = get_graphql_type_from_column(column.type)
    type_name = get_graphql_type_comparison_name(graphql_type)

    if type_name in inputs:
        return inputs[type_name]

    fields = get_base_comparison_fields(graphql_type)

    if graphql_type == GraphQLString:
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
        fields[column.name] = GraphQLInputField(get_graphql_type_from_column(column.type))

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
            fields[column.name] = GraphQLInputField(get_graphql_type_from_column(column.type))

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
        fields[column.name] = GraphQLInputField(GraphQLNonNull(get_graphql_type_from_column(column.type)))

    return GraphQLInputObjectType(type_name, fields)
