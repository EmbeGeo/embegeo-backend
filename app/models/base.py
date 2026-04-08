from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    """Base class which provides automated table name
    and represents the declarative base for SQLAlchemy models."""

    pass
