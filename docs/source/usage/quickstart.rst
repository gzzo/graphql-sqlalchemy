Quick Start
===========

This example sets up a barebones application serving a graphql endpoint. ::

    from ariadne.asgi import GraphQL
    from fastapi import FastAPI
    from sqlalchemy import create_engine
    from sqlalchemy.orm import declarative_base, sessionmaker
    from graphql_sqlalchemy import build_schema

    engine = create_engine('sqlite:///config.db')
    Base = declarative_base()
    Session = sessionmaker(bind=engine)

    app = FastAPI()
    session = Session()

    schema = build_schema(Base)

    app.mount("/graphql", GraphQL(schema, context_value=dict(session=session)))

.. highlight:: graphql

Now we can start writing queries, for example: ::

    query {
        user(
            where: {
                _or: [
                    { id: { _gte: 5 } },
                    { name: { _like: "%bob%" } },
                ]
            }
        ) {
            id
            name
        }
        user_by_pk(id: 5) {
            createtime
        }
    }

For more information on querying, see the :doc:`query reference </reference/query>`.

For an example application see: `graphql-sqlalchemy-example <https://github.com/gzzo/graphql-sqlalchemy-example>`_.
