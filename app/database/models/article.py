"""Article model — one collected news item, raw and cleaned text."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.analysis import AnalysisResult, WordFrequency
    from app.database.models.source import Source


class Article(Base):
    """A collected article. Deduplicated by `url` (unique).

    UA: Зібрана стаття. Дублікати усуваються за полем `url` (унікальне).
    """

    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), index=True
    )
    url: Mapped[str] = mapped_column(String(1000), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    raw_content: Mapped[str | None] = mapped_column(Text)
    cleaned_content: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime | None] = mapped_column(DateTime)
    collected_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    source: Mapped[Source] = relationship(back_populates="articles")
    analysis_results: Mapped[list[AnalysisResult]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )
    word_frequencies: Mapped[list[WordFrequency]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )
