"""Database engine, session factory, and table creation.

The engine reads its URL from `settings.database_url` (.env). For SQLite we
disable the same-thread check so the connection can be shared across FastAPI's
threadpool. `init_db()` imports the models package so every table is registered
on `Base.metadata` before `create_all`.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import settings
from app.database.base import Base

_is_sqlite = settings.database_url.startswith("sqlite")
_connect_args = {"check_same_thread": False} if _is_sqlite else {}

engine = create_engine(settings.database_url, connect_args=_connect_args, echo=False)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a session and always closes it.

    UA: Залежність FastAPI: видає сесію БД і завжди закриває її.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables. Importing models registers them on Base.metadata.

    UA: Створює всі таблиці. Імпорт моделей реєструє їх у Base.metadata.
    """
    from app.database import models  # noqa: F401  (side effect: register tables)

    Base.metadata.create_all(bind=engine)