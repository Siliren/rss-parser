"""API schemas for the analyze-a-URL feature.

UA: Схеми API для аналізу за URL.
"""

from __future__ import annotations

from pydantic import BaseModel

from app.schemas.analytics import LabelCount


class UrlAnalysisRequest(BaseModel):
    """Request body: the URL to analyze. / Тіло запиту: URL для аналізу."""

    url: str


class UrlAnalysisOut(BaseModel):
    """Analysis of one ad-hoc URL (not stored). / Аналіз довільного URL."""

    url: str
    title: str | None = None
    word_count: int
    sentiment_label: str
    sentiment_score: float
    topic: str
    top_words: list[LabelCount]
