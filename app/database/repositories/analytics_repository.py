"""Analytics repository — aggregate queries for the dashboard / API.

UA: Репозиторій аналітики: зведені запити для дашборду / API.

Read-only counting and grouping over the stored analysis.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models import AnalysisResult, Article, WordFrequency


class AnalyticsRepository:
    """Aggregate metrics across articles. Construct with a session.

    UA: Зведені метрики за статтями. Створюється з сесією.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def article_counts(self) -> tuple[int, int]:
        """Return (total articles, processed articles). / Усього та оброблено."""
        total = self.session.scalar(select(func.count(Article.id))) or 0
        processed = (
            self.session.scalar(
                select(func.count(Article.id)).where(Article.processed.is_(True))
            )
            or 0
        )
        return total, processed

    def sentiment_counts(self) -> dict[str, int]:
        """Count articles per sentiment label. / Кількість за тональністю."""
        rows = self.session.execute(
            select(AnalysisResult.sentiment_label, func.count()).group_by(
                AnalysisResult.sentiment_label
            )
        ).all()
        return {label: count for label, count in rows if label}

    def topic_counts(self) -> list[tuple[str, int]]:
        """Count articles per topic, most common first. / Кількість за темами."""
        rows = self.session.execute(
            select(AnalysisResult.topic, func.count())
            .group_by(AnalysisResult.topic)
            .order_by(func.count().desc())
        ).all()
        return [(topic, count) for topic, count in rows if topic]

    def top_words(self, limit: int = 20) -> list[tuple[str, int]]:
        """Most frequent words across all articles. / Найчастіші слова загалом."""
        total = func.sum(WordFrequency.count)
        rows = self.session.execute(
            select(WordFrequency.word, total)
            .group_by(WordFrequency.word)
            .order_by(total.desc())
            .limit(limit)
        ).all()
        return [(word, int(count)) for word, count in rows]
