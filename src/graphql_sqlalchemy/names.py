from typing import Union, Optional

from graphql import GraphQLList, GraphQLScalarType
from sqlalchemy import Column
from sqlalchemy.ext.declarative import DeclarativeMeta

from .helpers import get_table


FIELD_NAMES = {
    "by_pk": "%s_by_pk",
    "order_by": "%s_order_by",
    "where": "%s_bool_exp",
    "insert": "insert_%s",
    "insert_one": "insert_%s_one",
    "insert_input": "%s_insert_input",
    "mutation_response": "%s_mutation_response",
    "update": "update_%s",
    "update_by_pk": "update_%s_by_pk",
    "delete": "delete_%s",
    "delete_by_pk": "delete_%s_by_pk",
    "inc_input": "%s_inc_input",
    "set_input": "%s_set_input",
    "comparison": "%s_comparison_exp",
    "arr_comparison": "arr_%s_comparison_exp",
    "constraint": "%s_constraint",
    "update_column": "%s_update_column",
    "on_conflict": "%s_on_conflict",
    "pkey": "%s_pkey",
    "key": "%s_%s_key",
}


def get_table_name(model: Union[DeclarativeMeta, GraphQLScalarType, GraphQLList]) -> str:
    return get_table(model).name


def get_field_name(
    model: Union[DeclarativeMeta, GraphQLScalarType, GraphQLList],
    field_name: str,
    column: Optional[Union[Column, GraphQLScalarType, GraphQLList]] = None,
) -> str:
    if field_name == "comparison":
        if isinstance(model, GraphQLList):
            return FIELD_NAMES["arr_comparison"] % model.of_type.name.lower()
        else:
            return FIELD_NAMES[field_name] % getattr(model, "name").lower()

    else:
        name = get_table_name(model)
        if isinstance(column, Column) and field_name == "key":
            return FIELD_NAMES[field_name] % (name, column.name)

    return FIELD_NAMES[field_name] % name