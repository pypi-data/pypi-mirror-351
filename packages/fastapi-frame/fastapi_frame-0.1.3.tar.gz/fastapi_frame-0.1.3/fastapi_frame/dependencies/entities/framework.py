""" Framework entity representation for SQLAlchemy ORM. """

from enum import Enum
from sqlmodel import SQLModel, Field


class FrameworkTypes(Enum):
    """ Enum for framework types. """
    WEB_FRAMEWORK = 1
    API_FRAMEWORK = 2
    MICROSERVICE = 3
    ASYNC_FRAMEWORK = 4
    MIDDLEWARE = 5
    OTHER = 6


class Framework(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str


