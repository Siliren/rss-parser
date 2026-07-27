"""/analytics endpoint — aggregated metrics.

UA: Ендпоінт /analytics — зведені метрики.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.repositories import AnalyticsRepository
from app.database.session import get_db
from app.schemas import AnalyticsOut, LabelCount

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsOut)
def get_analytics(
    top_words: int = 20,
    db: Session = Depends(get_db),
) -> AnalyticsOut:
    """Aggregated metrics: counts, sentiment, topics, top words.

    UA: Зведені метрики: кількість, тональність, теми, топ слів.
    """
    repo = AnalyticsRepository(db)
    total, processed = repo.article_counts()
    return AnalyticsOut(
        total_articles=total,
        processed_articles=processed,
        sentiment=repo.sentiment_counts(),
        topics=[LabelCount(name=topic, count=count) for topic, count in repo.topic_counts()],
        top_words=[LabelCount(name=word, count=count) for word, count in repo.top_words(top_words)],
    )
