from typing import Optional, Dict

from graphql import (
    GraphQLArgument,
    GraphQLNonNull,
    GraphQLInputObjectType,
    GraphQLInt,
    GraphQLList,
    GraphQLEnumType,
    GraphQLInputField,
)
from sqlalchemy.ext.declarative import DeclarativeMeta

from .scalars import get_graphql_type_from_column
from .objects import get_comparison_object_type
from .names import get_model_order_by_input_name, get_model_where_input_name


PAGINATION_ARGS = {"limit": GraphQLInt, "offset": GraphQLInt}
ORDER_BY_ENUM = GraphQLEnumType("order_by", {"desc": "desc", "asc": "asc"})


def make_where_type(model: DeclarativeMeta, inputs: Dict[str, GraphQLInputObjectType]) -> GraphQLInputObjectType:
    type_name = get_model_where_input_name(model)

    def get_fields():
        fields = {
            "_and": GraphQLList(inputs[type_name]),
            "_or": GraphQLList(inputs[type_name]),
            "_not": inputs[type_name],
        }

        for column in model.__table__.columns:  # type: ignore
            fields[column.name] = GraphQLInputField(get_comparison_object_type(column, inputs))

        for name, relationship in model.__mapper__.relationships.items():
            fields[name] = inputs[get_model_where_input_name(relationship.mapper.entity)]

        return fields

    input_type = GraphQLInputObjectType(type_name, get_fields)
    inputs[type_name] = input_type
    return input_type


def make_order_type(model: DeclarativeMeta, inputs: Dict[str, GraphQLInputObjectType]) -> GraphQLInputObjectType:
    type_name = get_model_order_by_input_name(model)

    def get_fields():
        fields = {}

        for column in model.__table__.columns:  # type: ignore
            fields[column.name] = GraphQLInputField(ORDER_BY_ENUM)

        for name, relationship in model.__mapper__.relationships.items():
            fields[name] = inputs[get_model_order_by_input_name(relationship.mapper.entity)]

        return fields

    input_type = GraphQLInputObjectType(type_name, get_fields)
    inputs[type_name] = input_type
    return input_type


def make_args(model: DeclarativeMeta, inputs: Dict[str, GraphQLInputObjectType]) -> Dict[str, GraphQLArgument]:
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
