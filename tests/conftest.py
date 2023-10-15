from __future__ import annotations

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker


@pytest.fixture(scope="session")
def db_engine() -> Engine:
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)

    yield engine

    engine.dispose()


@pytest.fixture(scope="session")
def db_session_factory(db_engine: Engine) -> scoped_session:
    """returns a SQLAlchemy scoped session factory"""
    return scoped_session(sessionmaker(bind=db_engine))


@pytest.fixture()
def db_session(db_session_factory: scoped_session) -> Session:
    """yields a SQLAlchemy connection which is rollbacked after the test"""
    session = db_session_factory()

    yield session

    session.rollback()
    session.close()
