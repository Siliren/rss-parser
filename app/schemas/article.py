"""API response schema for an article.

UA: Схема відповіді API для статті.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ArticleOut(BaseModel):
    """An article plus its latest analysis, shaped for API responses.

    UA: Стаття разом з останнім аналізом для відповідей API.
    """

    id: int
    title: str
    url: str
    source: str
    published_at: datetime | None = None
    topic: str | None = None
    sentiment_label: str | None = None
    sentiment_score: float | None = None
