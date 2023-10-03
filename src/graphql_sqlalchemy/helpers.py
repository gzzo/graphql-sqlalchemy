from typing import List, Tuple

from sqlalchemy import Table
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Mapper, RelationshipProperty


def get_table(model: DeclarativeMeta) -> Table:
    return model.__table__


def get_mapper(model: DeclarativeMeta) -> Mapper:
    return model.__mapper__


def get_relationships(model: DeclarativeMeta) -> List[Tuple[str, RelationshipProperty]]:
    return get_mapper(model).relationships.items()
