from graphql_sqlalchemy import build_schema
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):  # type: ignore
    __tablename__ = "test"

    some_id = Column(Integer, primary_key=True)
    some_string = Column(String(length=320), unique=True, index=True, nullable=False)
    some_bool = Column(Boolean, nullable=False)
    some_int = Column(Integer, nullable=False)


schema = build_schema(Base)
