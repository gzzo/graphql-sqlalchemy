from sqlalchemy import Column
from sqlalchemy.ext.declarative import DeclarativeMeta
from graphql import GraphQLScalarType

from .helpers import get_table


def get_table_name(model: DeclarativeMeta) -> str:
    return get_table(model).name


def get_model_pk_field_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_by_pk"


def get_model_order_by_input_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_order_by"


def get_model_where_input_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_bool_exp"


def get_scalar_comparison_name(scalar: GraphQLScalarType) -> str:
    return f"{scalar.name.lower()}_comparison_exp"


def get_model_insert_input_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_insert_input"


def get_model_insert_object_name(model: DeclarativeMeta) -> str:
    return f"insert_{get_table_name(model)}"


def get_model_insert_one_object_name(model: DeclarativeMeta) -> str:
    return f"insert_{get_table_name(model)}_one"


def get_model_mutation_response_object_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_mutation_response"


def get_model_conflict_input_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_on_conflict"


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
