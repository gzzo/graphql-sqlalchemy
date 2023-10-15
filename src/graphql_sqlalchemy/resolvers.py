from __future__ import annotations

from functools import partial
from itertools import starmap
from typing import Any, Callable

from sqlalchemy import Column, and_, not_, or_, true
from sqlalchemy.orm import DeclarativeBase, Query, Session
from sqlalchemy.sql import ClauseElement


def make_field_resolver(field: str) -> Callable:
    def resolver(root: type[DeclarativeBase], _info: Any) -> Any:
        return getattr(root, field)

    return resolver


def get_bool_operation(model_property: Column, operator: str, value: Any) -> bool | ClauseElement:
    if operator == "_eq":
        return model_property == value

    if operator == "_in":
        return model_property.in_(value)

    if operator == "_is_null":
        return model_property.is_(None)

    if operator == "_like":
        return model_property.like(value)

    if operator == "_neq":
        return model_property != value

    if operator == "_nin":
        return model_property.notin_(value)

    if operator == "_nlike":
        return model_property.notlike(value)

    if operator == "_lt":
        return model_property < value

    if operator == "_gt":
        return model_property > value

    if operator == "_lte":
        return model_property <= value

    if operator == "_gte":
        return model_property >= value

    raise Exception("Invalid operator")


def get_filter_operation(model: type[DeclarativeBase], where: dict[str, Any]) -> ClauseElement:
    partial_filter = partial(get_filter_operation, model)

    for name, exprs in where.items():
        if name == "_or":
            return or_(*map(partial_filter, exprs))

        if name == "_not":
            return not_(partial_filter(exprs))

        if name == "_and":
            return and_(*map(partial_filter, exprs))

        model_property = getattr(model, name)
        partial_bool = partial(get_bool_operation, model_property)
        return and_(*(starmap(partial_bool, exprs.items())))

    return true()


def filter_query(model: type[DeclarativeBase], query: Query, where: dict[str, Any] | None = None) -> Query:
    if not where:
        return query

    query_filter = getattr(query, "filter")
    for name, exprs in where.items():
        query = query_filter(get_filter_operation(model, {name: exprs}))

    return query


def order_query(model: type[DeclarativeBase], query: Query, order: list[dict[str, Any]] | None = None) -> Query:
    if not order:
        return query

    for expr in order:
        for name, direction in expr.items():
            model_property = getattr(model, name)
            model_order = getattr(model_property, direction)
            query_order = getattr(query, "order_by")
            query = query_order(model_order())

    return query


def make_object_resolver(model: type[DeclarativeBase]) -> Callable:
    def resolver(
        _root: None,
        info: Any,
        where: dict[str, Any] | None = None,
        order: list[dict[str, Any]] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[type[DeclarativeBase]]:
        session = info.context["session"]
        query = session.query(model)

        query = filter_query(model, query, where)
        query = order_query(model, query, order)

        if limit:
            query = getattr(query, "limit")(limit)

        if offset:
            query = getattr(query, "offset")(offset)

        return query.all()

    return resolver


def make_pk_resolver(model: type[DeclarativeBase]) -> Callable:
    def resolver(_root: None, info: Any, **kwargs: dict[str, Any]) -> type[DeclarativeBase]:
        session = info.context["session"]
        return session.query(model).get(kwargs)

    return resolver


def session_add_object(
    obj: dict[str, Any], model: type[DeclarativeBase], session: Session, on_conflict: dict[str, Any] | None = None
) -> type[DeclarativeBase]:
    instance = model()
    for key, value in obj.items():
        setattr(instance, key, value)

    if on_conflict and on_conflict["merge"]:
        session.merge(instance)
    else:
        session.add(instance)
    return instance


def session_commit(session: Session) -> None:
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise


def make_insert_resolver(model: type[DeclarativeBase]) -> Callable:
    def resolver(
        _root: None, info: Any, objects: list[dict[str, Any]], on_conflict: dict[str, Any] | None = None
    ) -> dict[str, int | list[type[DeclarativeBase]]]:
        session = info.context["session"]
        models = []

        with session.no_autoflush:
            for obj in objects:
                instance = session_add_object(obj, model, session, on_conflict)
                models.append(instance)

        session_commit(session)
        return {"affected_rows": len(models), "returning": models}

    return resolver


def make_insert_one_resolver(model: type[DeclarativeBase]) -> Callable:
    def resolver(
        _root: None, info: Any, object: dict[str, Any], on_conflict: dict[str, Any] | None = None
    ) -> type[DeclarativeBase]:
        session = info.context["session"]

        instance = session_add_object(object, model, session, on_conflict)
        session_commit(session)
        return instance

    return resolver


def make_delete_resolver(model: type[DeclarativeBase]) -> Callable:
    def resolver(
        _root: None, info: Any, where: dict[str, Any] | None = None
    ) -> dict[str, int | list[type[DeclarativeBase]]]:
        session = info.context["session"]
        query = session.query(model)
        query = filter_query(model, query, where)

        rows = query.all()
        affected = query.delete()
        session_commit(session)

        return {"affected_rows": affected, "returning": rows}

    return resolver


def make_delete_by_pk_resolver(model: type[DeclarativeBase]) -> Callable:
    def resolver(_root: None, info: Any, **kwargs: dict[str, Any]) -> list[type[DeclarativeBase]] | None:
        session = info.context["session"]

        row = session.query(model).get(kwargs)
        if row:
            session.delete(row)
            session_commit(session)
            return row

        return None

    return resolver


def update_query(
    query: Query,
    model: type[DeclarativeBase],
    _set: dict[str, Any] | None = None,
    _inc: dict[str, Any] | None = None,
) -> int:
    affected = 0
    if _inc:
        to_increment = {}
        for column_name, increment in _inc.items():
            to_increment[column_name] = getattr(model, column_name) + increment

        affected += query.update(to_increment)

    if _set:
        affected += query.update(_set)

    return affected


def make_update_resolver(model: type[DeclarativeBase]) -> Callable:
    def resolver(
        _root: None,
        info: Any,
        where: dict[str, Any],
        _set: dict[str, Any] | None,
        _inc: dict[str, Any] | None,
    ) -> dict[str, int | list[type[DeclarativeBase]]]:
        session = info.context["session"]
        query = session.query(model)
        query = filter_query(model, query, where)
        affected = update_query(query, model, _set, _inc)
        session_commit(session)

        return {
            "affected_rows": affected,
            "returning": query.all(),
        }

    return resolver


def make_update_by_pk_resolver(model: type[DeclarativeBase]) -> Callable:
    def resolver(
        _root: None,
        info: Any,
        _set: dict[str, Any] | None,
        _inc: dict[str, Any] | None,
        **pk_columns: dict[str, Any],
    ) -> type[DeclarativeBase] | None:
        session = info.context["session"]
        query = session.query(model).filter_by(**pk_columns)

        if update_query(query, model, _set, _inc):
            session_commit(session)
            return query.one()

        return None

    return resolver
