from sqlalchemy.ext.declarative import DeclarativeMeta


def get_table_name(model: DeclarativeMeta) -> str:
    return model.__tablename__  # type: ignore


def get_model_pk_field_name(model: DeclarativeMeta) -> str:
    return f"{get_table_name(model)}_by_pk"
