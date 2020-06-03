[![PyPI version](https://badge.fury.io/py/graphql-sqlalchemy.svg)](https://badge.fury.io/py/graphql-sqlalchemy)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Generate GraphQL Schemas from your SQLAlchemy models

# Install
```
pip install graphql-sqlalchemy
```

# Usage

```python
from ariadne import QueryType
from ariadne.asgi import GraphQL
from fastapi import FastAPI
from graphql_sqlalchemy import build_schema

from .session import Session
from .base import Base


app = FastAPI()
query = QueryType()
session = Session()

schema = build_schema(Base)
query.bind_to_schema(schema)

app.mount("/graphql", GraphQL(schema, context_value=dict(session=session)))
```
