from advanced_alchemy.base import AuditColumns
from pydantic import BaseModel as _BaseModel
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase, AuditColumns):
    """Base for SQLAlchemy declarative models in this project with int primary keys."""


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {'from_attributes': True}
