"""Source model — a news site or Telegram channel we collect from."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.article import Article


class Source(Base):
    """A content source. One source has many articles.

    UA: Джерело контенту (новинний сайт або Telegram-канал). Має багато статей.
    """

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    base_url: Mapped[str] = mapped_column(String(500))
    type: Mapped[str] = mapped_column(String(30), default="news")  # news | telegram
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    articles: Mapped[list[Article]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )