"""API response schema for a collection run.

UA: Схема відповіді API для запуску збору.
"""

from __future__ import annotations

from pydantic import BaseModel


class CollectResponse(BaseModel):
    """Result of running the pipeline for one source.

    UA: Результат запуску конвеєра для одного джерела.
    """

    source: str
    fetched: int
    saved: int
    processed: int
