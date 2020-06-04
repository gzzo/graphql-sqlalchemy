from typing import Any, Callable, Dict, List

from sqlalchemy.orm import Query
from sqlalchemy.ext.declarative import DeclarativeMeta


def make_field_resolver(field: str) -> Callable:
    def resolver(root: DeclarativeMeta, _info: Any):
        return getattr(root, field)

    return resolver


def filter_query(model: DeclarativeMeta, query: Query, where: Dict[str, Any] = None) -> Query:
    if not where:
        return query

    for name, exprs in where.items():
        model_property = getattr(model, name)
        query_filter = getattr(query, "filter")

        for operator, value in exprs.items():
            if operator == "_eq":
                query = query_filter(model_property == value)
            elif operator == "_in":
                query = query_filter(model_property.in_(value))
            elif operator == "_is_null":
                query = query_filter(model_property.is_(None))
            elif operator == "_like":
                query = query_filter(model_property.like(value))
            elif operator == "_neq":
                query = query_filter(model_property != value)
            elif operator == "_nin":
                query = query_filter(model_property.notin_(value))
            elif operator == "_nlike":
                query = query_filter(model_property.notlike(value))
            elif operator == "_lt":
                query = query_filter(model_property < value)
            elif operator == "_gt":
                query = query_filter(model_property > value)
            elif operator == "_lte":
                query = query_filter(model_property <= value)
            elif operator == "_gte":
                query = query_filter(model_property >= value)

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
