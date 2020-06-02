from typing import Any, Callable, Dict

from sqlalchemy.ext.declarative import DeclarativeMeta


def make_field_resolver(field: str) -> Callable:
    def resolver(root: DeclarativeMeta, _info: Any):
        return getattr(root, field)

    return resolver


def make_resolver(model: DeclarativeMeta) -> Callable:
    def resolver(_root: DeclarativeMeta, info: Any):
        session = info.context["session"]
        return session.query(model).all()

    return resolver


def make_pk_resolver(model: DeclarativeMeta) -> Callable:
    def resolver(_root: DeclarativeMeta, info: Any, **kwargs: Dict[str, Any]):
        session = info.context["session"]
        return session.query(model).get(kwargs)

    return resolver
