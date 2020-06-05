# graphql-sqlalchemy

[![PyPI version](https://badge.fury.io/py/graphql-sqlalchemy.svg)](https://badge.fury.io/py/graphql-sqlalchemy)
[![Build Status](https://travis-ci.com/gzzo/graphql-sqlalchemy.svg?branch=master)](https://travis-ci.com/gzzo/graphql-sqlalchemy)
[![codecov](https://codecov.io/gh/gzzo/graphql-sqlalchemy/branch/master/graph/badge.svg)](https://codecov.io/gh/gzzo/graphql-sqlalchemy)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Generate GraphQL Schemas from your SQLAlchemy models

# Install
```
pip install graphql-sqlalchemy
```

# Usage

```python
from ariadne.asgi import GraphQL
from fastapi import FastAPI
from graphql_sqlalchemy import build_schema

from .session import Session
from .base import Base


app = FastAPI()
session = Session()

schema = build_schema(Base)

app.mount("/graphql", GraphQL(schema, context_value=dict(session=session)))
```

# Query

```graphql
query MyQuery {
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
    model_by_pk(id: 5) {
        createtime
    }
}
```
