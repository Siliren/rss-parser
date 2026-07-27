"""API response schemas for analytics.

UA: Схеми відповідей API для аналітики.
"""

from __future__ import annotations

from pydantic import BaseModel


class LabelCount(BaseModel):
    """A name and how many times it occurs. / Назва та її кількість."""

    name: str
    count: int


class AnalyticsOut(BaseModel):
    """Aggregated metrics across all stored articles.

    UA: Зведені метрики за всіма збереженими статтями.
    """

    total_articles: int
    processed_articles: int
    sentiment: dict[str, int]  # label -> count
    topics: list[LabelCount]
    top_words: list[LabelCount]
