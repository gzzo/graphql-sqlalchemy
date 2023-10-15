from __future__ import annotations

import sys
from collections.abc import Callable
from typing import Any, Literal

import pytest
from graphql import GraphQLSchema, graphql_sync
from graphql_sqlalchemy.schema import build_schema
from sqlalchemy import Engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, registry, relationship

if sys.version_info < (3, 11):
    from exceptiongroup import ExceptionGroup


class Base(DeclarativeBase):
    registry = registry()


class Author(Base):
    __tablename__ = "author"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    articles: Mapped[list[Article]] = relationship(back_populates="author")


class Article(Base):
    __tablename__ = "article"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"))
    author: Mapped[Author] = relationship(back_populates="articles")
    rating: Mapped[int]


@pytest.fixture(scope="session")
def gql_schema() -> GraphQLSchema:
    return build_schema(Base)


@pytest.fixture()
def example_session(db_engine: Engine, db_session: Session) -> Session:
    Base.metadata.create_all(bind=db_engine)
    with db_session.begin():
        db_session.add(felicias := Author(name="Felicitas"))
        db_session.add_all(
            [
                Article(title="Felicitas good", author=felicias, rating=4),
                Article(title="Felicitas better", author=felicias, rating=5),
            ]
        )
        db_session.add(bjork := Author(name="Björk"))
        db_session.add_all(
            [
                Article(title="Björk bad", author=bjork, rating=2),
                Article(title="Björk good", author=bjork, rating=4),
            ]
        )
        db_session.add(lundth := Author(name="Lundth"))
        db_session.add_all(
            [
                Article(title="Lundth bad", author=lundth, rating=1),
            ]
        )
        db_session.commit()
    return db_session


@pytest.fixture()
def query_example(example_session: Session, gql_schema: GraphQLSchema) -> Callable[[str], Any]:
    def query(source: str) -> Any:
        result = graphql_sync(gql_schema, source, context_value={"session": example_session})
        if result.errors:
            raise result.errors[0] if len(result.errors) == 1 else ExceptionGroup("Invalid Query", result.errors)
        return result.data

    return query


def test_all(query_example: Callable[[str], Any]) -> None:
    data = query_example("query { author { name } }")
    author_names = {author["name"] for author in data["author"]}
    assert author_names == {"Felicitas", "Björk", "Lundth"}


@pytest.mark.parametrize(
    "filter",
    [
        pytest.param("both", marks=pytest.mark.xfail(reason="Both not implemented")),
        pytest.param("author", marks=pytest.mark.xfail(reason="nested conditions not implemented")),
        pytest.param("article", marks=pytest.mark.xfail(reason="conditions on nested fields not implemented")),
    ],
)
def test_highly_rated(
    query_example: Callable[[str], Any],
    filter: Literal["both", "author", "article"],
) -> None:
    author_filter = "(where: { articles: { rating: { _gt: 4 } } })" if filter != "article" else ""
    article_filter = "(where: { rating: { _gt: 4 } })" if filter != "author" else ""
    data = query_example(
        f"""
        query {{
            author{author_filter} {{
                id
                name
                articles{article_filter} {{
                    id
                    title
                    rating
                }}
            }}
        }}
        """
    )
    author_names = {author["name"] for author in data["author"]}
    if author_filter:
        assert author_names == {"Felicitas", "Björk"}
    else:
        assert len(author_names) == 3

    articles = {article for author in data["author"] for article in author["articles"]}
    article_titles = {article["title"] for article in articles}
    if article_filter:
        assert article_titles == {"Felicitas good", "Felicitas better", "Björk good"}
    else:
        assert len(article_titles) == 5
