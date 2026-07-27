"""/articles endpoints — list stored articles.

UA: Ендпоінти /articles — список збережених статей.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.models import Article
from app.database.repositories import ArticleRepository
from app.database.session import get_db
from app.schemas import ArticleOut

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=list[ArticleOut])
def list_articles(
    source_id: int | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[ArticleOut]:
    """List recent articles, newest first; optional filter by source.

    UA: Список останніх статей (спершу новіші); фільтр за джерелом — опційно.
    """
    articles = ArticleRepository(db).get_articles(source_id=source_id, limit=limit)
    return [_to_out(article) for article in articles]


def _to_out(article: Article) -> ArticleOut:
    """Flatten an Article + its latest analysis into the API shape.

    UA: Зводить Article та його останній аналіз у форму для API.
    """
    analysis = article.analysis_results[0] if article.analysis_results else None
    return ArticleOut(
        id=article.id,
        title=article.title,
        url=article.url,
        source=article.source.name,
        published_at=article.published_at,
        topic=analysis.topic if analysis else None,
        sentiment_label=analysis.sentiment_label if analysis else None,
        sentiment_score=analysis.sentiment_score if analysis else None,
    )
