from sqlalchemy.ext.declarative import DeclarativeMeta
from graphql import GraphQLScalarType


def get_table_name(model: DeclarativeMeta) -> str:
    return model.__tablename__  # type: ignore


def get_model_pk_field_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_by_pk"


def get_model_order_by_input_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_order_by"


def get_model_where_input_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_bool_exp"


def get_scalar_comparison_name(scalar: GraphQLScalarType) -> str:
    return f"{scalar.name.lower()}_comparison_exp"
