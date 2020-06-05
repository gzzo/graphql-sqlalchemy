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


def get_model_mutation_response_object_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_mutation_response"
