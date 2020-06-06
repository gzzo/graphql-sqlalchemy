from sqlalchemy.ext.declarative import DeclarativeMeta
from graphql import (
    GraphQLInputObjectType,
    GraphQLList,
    GraphQLEnumType,
    GraphQLInputField,
    GraphQLNonNull,
)

from ...names import (
    get_model_conflict_input_name,
    get_model_constraint_enum_name,
    get_model_constraint_key_name,
    get_model_column_update_enum_name,
)
from ...types import Inputs
from ...helpers import get_table
from ...inputs import get_where_input_type


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
        "where": GraphQLInputField(get_where_input_type(model, inputs)),
    }

    input_type = GraphQLInputObjectType(type_name, fields)
    inputs[type_name] = input_type
    return input_type
