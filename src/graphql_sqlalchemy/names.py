from __future__ import annotations

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


def get_model_order_by_input_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_order_by"


def get_model_where_input_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_bool_exp"


def get_graphql_type_comparison_name(graphql_type: GraphQLList[GraphQLScalarType] | GraphQLScalarType) -> str:
    if isinstance(graphql_type, GraphQLList):
        return f"arr_{graphql_type.of_type.name.lower()}_comparison_exp"

    return f"{graphql_type.name.lower()}_comparison_exp"


def get_model_insert_input_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_insert_input"


def get_model_insert_object_name(model: DeclarativeMeta) -> str:
    return f"insert_{get_table_name(model)}"


def get_model_insert_one_object_name(model: DeclarativeMeta) -> str:
    return f"insert_{get_table_name(model)}_one"


def get_model_conflict_input_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_on_conflict"


def get_model_mutation_response_object_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_mutation_response"


def get_model_constraint_enum_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_constraint"


def get_model_constraint_key_name(model: DeclarativeMeta, column: Column, is_primary_key: bool = False) -> str:
    if is_primary_key:
        return f"{get_table_name(model)}_pkey"

    return f"{get_table_name(model)}_{column.name}_key"


def get_model_column_update_enum_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_update_column"


def get_model_delete_name(model: DeclarativeMeta) -> str:
    return f"delete_{get_table_name(model)}"


def get_model_delete_by_pk_name(model: DeclarativeMeta) -> str:
    return f"delete_{get_table_name(model)}_by_pk"


def get_model_update_name(model: DeclarativeMeta) -> str:
    return f"update_{get_table_name(model)}"


def get_model_update_by_pk_name(model: DeclarativeMeta) -> str:
    return f"update_{get_table_name(model)}_by_pk"


def get_model_inc_input_type_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_inc_input"


def get_model_set_input_type_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_set_input"


def get_model_pk_columns_input_type_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_pk_columns_input"
