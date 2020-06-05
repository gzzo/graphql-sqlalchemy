from typing import List, Tuple

from sqlalchemy import Table
from sqlalchemy.orm import Mapper, RelationshipProperty
from sqlalchemy.ext.declarative import DeclarativeMeta


def get_table(model: DeclarativeMeta) -> Table:
    return model.__table__  # type: ignore


def get_mapper(model: DeclarativeMeta) -> Mapper:
    return model.__mapper__  # type: ignore


def get_relationships(model: DeclarativeMeta) -> List[Tuple[str, RelationshipProperty]]:
    return get_mapper(model).relationships.items()  # type: ignore
