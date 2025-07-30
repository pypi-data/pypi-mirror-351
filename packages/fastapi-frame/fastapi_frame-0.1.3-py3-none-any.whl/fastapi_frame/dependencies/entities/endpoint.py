""" Endpoint entity representation for SQLAlchemy ORM. """

from typing import Optional
from sqlmodel import SQLModel, Field


class Endpoint(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    description: Optional[str] = None
    method: str
    framework_id: int = Field(foreign_key="framework.id")
