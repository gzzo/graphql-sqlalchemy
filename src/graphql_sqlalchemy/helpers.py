from __future__ import annotations

from sqlalchemy import Float, Integer, Table
from sqlalchemy.orm import DeclarativeBase, Mapper, RelationshipProperty


def get_table(model: type[DeclarativeBase]) -> Table:
    return model.__table__


def get_mapper(model: type[DeclarativeBase]) -> Mapper:
    return model.__mapper__


def get_relationships(model: type[DeclarativeBase]) -> list[tuple[str, RelationshipProperty]]:
    return get_mapper(model).relationships.items()


def has_int(model: type[DeclarativeBase]) -> bool:
    return any([isinstance(i.type, (Integer, Float)) for i in get_table(model).columns])
