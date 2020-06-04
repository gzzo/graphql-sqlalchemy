from typing import Any, Callable, Dict, List

from sqlalchemy.ext.declarative import DeclarativeMeta


def make_field_resolver(field: str) -> Callable:
    def resolver(root: DeclarativeMeta, _info: Any):
        return getattr(root, field)

    return resolver


def make_resolver(model: DeclarativeMeta) -> Callable:
    def resolver(
        _root: DeclarativeMeta,
        info: Any,
        order: List[Dict[str, Any]] = None,
        limit: int = None,
        offset: int = None,
        **_kwargs: Dict[str, Any],
    ):
        order = order or []
        session = info.context["session"]
        query = session.query(model)

        for expr in order:
            for name, direction in expr.items():
                model_property = getattr(model, name)
                model_order = getattr(model_property, direction)
                query_order = getattr(query, "order_by")
                query = query_order(model_order())

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
