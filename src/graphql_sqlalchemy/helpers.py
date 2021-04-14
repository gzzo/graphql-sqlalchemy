from typing import List, Tuple, Any

from sqlalchemy import Table, Integer, Float
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Mapper, RelationshipProperty


def get_table(model: DeclarativeMeta) -> Table:
    return model.__table__  # type: ignore


def get_mapper(model: DeclarativeMeta) -> Mapper:
    return model.__mapper__  # type: ignore


def get_relationships(model: DeclarativeMeta) -> List[Tuple[str, RelationshipProperty]]:
    return get_mapper(model).relationships.items()  # type: ignore


def has_int(model: DeclarativeMeta) -> bool:
    return any([isinstance(i.type, (Integer, Float)) for i in get_table(model).columns])


def get_pk_columns(model: DeclarativeMeta) -> Any:
    return [column for column in get_table(model).primary_key]
