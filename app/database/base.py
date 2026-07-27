"""Declarative base for all ORM models.

Kept separate from session.py so models can import `Base` without
pulling in the engine (avoids import cycles).
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base. All models inherit from this."""