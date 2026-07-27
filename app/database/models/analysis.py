"""Analysis models — NLP results derived from an article.

AnalysisResult holds per-article metrics (sentiment, topic, word count).
WordFrequency holds one row per (article, word) for the word-cloud / frequency
views. Both are written by the analysis stage (Stage 6+).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.article import Article


class AnalysisResult(Base):
    """One analysis pass over an article.

    UA: Результат аналізу однієї статті (тональність, тема, кількість слів).
    """

    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"), index=True
    )
    sentiment_label: Mapped[str | None] = mapped_column(String(20))  # positive|neutral|negative
    sentiment_score: Mapped[float | None] = mapped_column(Float)
    topic: Mapped[str | None] = mapped_column(String(100))
    word_count: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    article: Mapped[Article] = relationship(back_populates="analysis_results")


class WordFrequency(Base):
    """Count of one lemma within one article.

    UA: Скільки разів слово (лема) трапляється в одній статті.
    """

    __tablename__ = "word_frequencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"), index=True
    )
    word: Mapped[str] = mapped_column(String(100), index=True)
    count: Mapped[int] = mapped_column(Integer, default=1)

    article: Mapped[Article] = relationship(back_populates="word_frequencies")
