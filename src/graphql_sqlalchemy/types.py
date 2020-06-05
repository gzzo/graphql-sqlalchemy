from typing import Dict

from graphql import GraphQLObjectType, GraphQLInputObjectType, GraphQLField

Objects = Dict[str, GraphQLObjectType]
Inputs = Dict[str, GraphQLInputObjectType]
Fields = Dict[str, GraphQLField]
