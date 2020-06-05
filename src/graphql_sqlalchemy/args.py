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

from .types import get_graphql_type_from_column, get_comparison_object_type
from .names import get_table_name, get_model_order_by_input_name


PAGINATION_ARGS = {"limit": GraphQLInt, "offset": GraphQLInt}
ORDER_BY_ENUM = GraphQLEnumType("order_by", {"desc": "desc", "asc": "asc"})


def make_where_type(model: DeclarativeMeta, inputs: Dict[str, GraphQLInputObjectType]) -> GraphQLInputObjectType:
    type_name = f"{get_table_name(model)}_bool_exp"
    fields = {}

    for column in model.__table__.columns:  # type: ignore
        fields[column.name] = GraphQLInputField(get_comparison_object_type(column, inputs))

    return GraphQLInputObjectType(type_name, fields)


def make_order_type(model: DeclarativeMeta, inputs: Dict[str, GraphQLInputObjectType]) -> GraphQLInputObjectType:
    type_name = get_model_order_by_input_name(model)

    def get_fields():
        fields = {}

        for column in model.__table__.columns:  # type: ignore
            fields[column.name] = GraphQLInputField(ORDER_BY_ENUM)

        for name, relationship in model.__mapper__.relationships.items():
            fields[name] = inputs[get_model_order_by_input_name(relationship.mapper.entity)]

        return fields

    return GraphQLInputObjectType(type_name, get_fields)


def make_args(model: DeclarativeMeta, inputs: Dict[str, GraphQLInputObjectType]) -> Dict[str, GraphQLArgument]:
    args = {}
    for name, field in PAGINATION_ARGS.items():
        args[name] = GraphQLArgument(field)

    order_type = make_order_type(model, inputs)
    inputs[order_type.name] = order_type
    args["order"] = GraphQLArgument(GraphQLList(GraphQLNonNull(order_type)))
    args["where"] = GraphQLArgument(make_where_type(model, inputs=inputs))

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
