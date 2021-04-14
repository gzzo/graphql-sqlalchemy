from graphql import (
    GraphQLBoolean,
    GraphQLEnumType,
    GraphQLInputField,
    GraphQLInputFieldMap,
    GraphQLInputObjectType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLScalarType,
    GraphQLString,
)
from sqlalchemy import Float, Integer

from typing import Any, Union
from .graphql_types import get_graphql_type_from_column
from .helpers import get_relationships, get_table
from .names import get_field_name
from .types import Inputs


ORDER_BY_ENUM = GraphQLEnumType("order_by", {"desc": "desc", "asc": "asc"})


def get_type_comparison_fields(graphql_type: Union[GraphQLScalarType, GraphQLList], inputs: Inputs, type_name: str) -> GraphQLInputObjectType:
    if type_name in inputs:
        return inputs[type_name]

    fields = {
        "_eq": GraphQLInputField(graphql_type),
        "_neq": GraphQLInputField(graphql_type),
        "_in": GraphQLInputField(GraphQLList(GraphQLNonNull(graphql_type))),
        "_nin": GraphQLInputField(GraphQLList(GraphQLNonNull(graphql_type))),
        "_lt": GraphQLInputField(graphql_type),
        "_gt": GraphQLInputField(graphql_type),
        "_gte": GraphQLInputField(graphql_type),
        "_lte": GraphQLInputField(graphql_type),
        "_is_null": GraphQLInputField(GraphQLBoolean),
    }

    fields_string = {
        "_like": GraphQLInputField(GraphQLString),
        "_nlike": GraphQLInputField(GraphQLString),
    }

    if graphql_type == GraphQLString:
        fields.update(fields_string)

    inputs[type_name] = GraphQLInputObjectType(type_name, fields)
    return inputs[type_name]


def get_input_type(model: Any, inputs: Inputs, input_type: Any) -> GraphQLInputObjectType:
    type_name = get_field_name(model, input_type)

    """ skip if field already exists """
    if type_name in inputs:
        return inputs[type_name]

    def get_fields() -> GraphQLInputFieldMap:
        """ initial field population """
        input_field = {
            "where": {
                "_and": GraphQLInputField(GraphQLList(inputs[type_name])),
                "_or": GraphQLInputField(GraphQLList(inputs[type_name])),
                "_not": GraphQLInputField(inputs[type_name]),
            },
            "on_conflict": {
                "merge": GraphQLInputField(GraphQLNonNull(GraphQLBoolean)),
            },
        }

        if input_type in input_field.keys():
            fields = input_field[input_type]
        else:
            fields = {}

        """ per column population """
        for column in get_table(model).columns:
            graphql_type = get_graphql_type_from_column(column.type)
            column_type = GraphQLInputField(graphql_type)

            input_field = {
                "where": GraphQLInputField(get_type_comparison_fields(graphql_type, inputs, get_field_name(graphql_type, "comparison"))),  # type: ignore
                "order_by": GraphQLInputField(ORDER_BY_ENUM),  # type: ignore
                "insert_input": column_type,  # type: ignore
                "inc_input": column_type if isinstance(column.type, (Integer, Float)) else None,  # type: ignore
                "set_input": column_type,  # type: ignore
            }

            if input_type in input_field.keys() and input_field[input_type]:
                fields[column.name] = input_field[input_type]  # type: ignore

        """ relationship population """
        for name, relationship in get_relationships(model):
            input_field = {
                "where": GraphQLInputField(inputs[get_field_name(relationship.mapper.entity, "where")]),  # type: ignore
                "order_by": GraphQLInputField(inputs[get_field_name(relationship.mapper.entity, "order_by")]),  # type: ignore
            }

            if input_type in input_field.keys():
                fields[name] = input_field[input_type]  # type: ignore

        return fields

    inputs[type_name] = GraphQLInputObjectType(type_name, get_fields)
    return inputs[type_name]
