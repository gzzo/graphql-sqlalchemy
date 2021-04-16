from typing import List, Tuple, Union

from graphql import GraphQLList, GraphQLScalarType
from sqlalchemy import Table, Integer, Float
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Mapper, RelationshipProperty


def get_table(model: Union[DeclarativeMeta, GraphQLScalarType, GraphQLList]) -> Table:
    return getattr(model, "__table__")


def get_mapper(model: DeclarativeMeta) -> Mapper:
    return getattr(model, "__mapper__")


def get_relationships(model: DeclarativeMeta) -> List[Tuple[str, RelationshipProperty]]:
    return getattr(get_mapper(model).relationships, "items")()


def has_int(model: DeclarativeMeta) -> bool:
    return any([isinstance(i.type, (Integer, Float)) for i in get_table(model).columns])
