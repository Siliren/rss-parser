"""/analyze endpoint — analyze any article URL on demand (stateless).

UA: Ендпоінт /analyze — аналіз будь-якої статті за URL (без збереження).

Nothing is saved to the database. The URL is validated against SSRF first.
"""

from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException

from app.schemas import LabelCount, UrlAnalysisOut, UrlAnalysisRequest
from app.services import analyze_url
from app.utils.url_safety import UnsafeUrlError

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=UrlAnalysisOut)
def analyze(request: UrlAnalysisRequest) -> UrlAnalysisOut:
    """Fetch and analyze the given URL; return metrics without storing them.

    UA: Завантажує та аналізує заданий URL; повертає метрики без збереження.
    """
    try:
        result = analyze_url(request.url)
    except UnsafeUrlError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"could not fetch URL: {exc}") from exc

    return UrlAnalysisOut(
        url=result.url,
        title=result.title,
        word_count=result.word_count,
        sentiment_label=result.sentiment_label,
        sentiment_score=result.sentiment_score,
        topic=result.topic,
        top_words=[LabelCount(name=word, count=count) for word, count in result.top_words],
    )
