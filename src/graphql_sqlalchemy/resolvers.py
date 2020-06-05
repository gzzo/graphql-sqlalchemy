from functools import partial
from itertools import starmap
from typing import Any, Callable, Dict, List, Union

from sqlalchemy import Column, or_, and_, not_, true
from sqlalchemy.sql import ClauseElement
from sqlalchemy.orm import Query
from sqlalchemy.ext.declarative import DeclarativeMeta


def make_field_resolver(field: str) -> Callable:
    def resolver(root: DeclarativeMeta, _info: Any):
        return getattr(root, field)

    return resolver


def get_bool_operation(model_property: Column, operator: str, value: Any) -> Union[bool, ClauseElement]:
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


def get_filter_operation(model: DeclarativeMeta, where: Dict[str, Any]) -> ClauseElement:
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


def filter_query(model: DeclarativeMeta, query: Query, where: Dict[str, Any] = None) -> Query:
    if not where:
        return query

    query_filter = getattr(query, "filter")
    for name, exprs in where.items():
        query = query_filter(get_filter_operation(model, {name: exprs}))

    return query


def order_query(model: DeclarativeMeta, query: Query, order: List[Dict[str, Any]] = None) -> Query:
    if not order:
        return query

    for expr in order:
        for name, direction in expr.items():
            model_property = getattr(model, name)
            model_order = getattr(model_property, direction)
            query_order = getattr(query, "order_by")
            query = query_order(model_order())

    return query


def make_resolver(model: DeclarativeMeta) -> Callable:
    def resolver(
        _root: DeclarativeMeta,
        info: Any,
        where: Dict[str, Any] = None,
        order: List[Dict[str, Any]] = None,
        limit: int = None,
        offset: int = None,
    ):
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


def make_pk_resolver(model: DeclarativeMeta) -> Callable:
    def resolver(_root: DeclarativeMeta, info: Any, **kwargs: Dict[str, Any]):
        session = info.context["session"]
        return session.query(model).get(kwargs)

    return resolver
