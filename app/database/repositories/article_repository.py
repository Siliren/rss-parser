"""Article repository — the one place that saves and reads articles.

UA: Репозиторій статей: єдине місце, де статті зберігаються та читаються.

Collectors hand us `RawArticle` objects; here we store them (dedup by `url`)
and read them back. No NLP, no HTTP — just the database.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.collectors.base import RawArticle
from app.database.models import AnalysisResult, Article, Source, WordFrequency


class ArticleRepository:
    """Save and query articles. Construct it with an active session.

    UA: Зберігає й читає статті. Створюється з активною сесією SQLAlchemy.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_create_source(
        self, name: str, base_url: str, *, source_type: str = "news"
    ) -> Source:
        """Return the source with this name, creating it if it's new.

        UA: Повертає джерело з такою назвою; створює, якщо його ще немає.
        """
        source = self.session.scalar(select(Source).where(Source.name == name))
        if source is None:
            source = Source(name=name, base_url=base_url, type=source_type)
            self.session.add(source)
            self.session.commit()
        return source

    def save_articles(
        self, source: Source, raw_articles: list[RawArticle]
    ) -> list[Article]:
        """Save new articles for a source, skipping URLs already stored.

        UA: Зберігає нові статті джерела, пропускаючи вже збережені URL.

        Returns only the newly-created articles (so the caller sees how many
        were actually new).
        """
        urls = [raw.url for raw in raw_articles]
        if not urls:
            return []

        already_stored = set(
            self.session.scalars(select(Article.url).where(Article.url.in_(urls))).all()
        )

        new_articles: list[Article] = []
        seen_in_batch: set[str] = set()
        for raw in raw_articles:
            if raw.url in already_stored or raw.url in seen_in_batch:
                continue  # dedup / усунення дублікатів
            seen_in_batch.add(raw.url)
            new_articles.append(
                Article(
                    source=source,
                    url=raw.url,
                    title=raw.title,
                    raw_content=raw.raw_content,
                    published_at=raw.published_at,
                )
            )

        if new_articles:
            self.session.add_all(new_articles)
            self.session.commit()
        return new_articles

    def get_articles(
        self, *, source_id: int | None = None, limit: int = 50
    ) -> list[Article]:
        """Read recent articles, newest first; optional filter by source.

        UA: Читає останні статті (спершу новіші); фільтр за джерелом — опційно.
        """
        stmt = select(Article).order_by(
            Article.collected_at.desc(), Article.id.desc()
        )
        if source_id is not None:
            stmt = stmt.where(Article.source_id == source_id)
        return list(self.session.scalars(stmt.limit(limit)).all())

    def get_unprocessed_articles(self, limit: int | None = None) -> list[Article]:
        """Read articles that have not been analyzed yet (oldest first).

        UA: Читає ще не проаналізовані статті (спершу старіші).
        """
        stmt = (
            select(Article)
            .where(Article.processed.is_(False))
            .order_by(Article.id)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(self.session.scalars(stmt).all())

    def save_analysis(
        self,
        article: Article,
        *,
        cleaned_content: str,
        sentiment_label: str,
        sentiment_score: float,
        topic: str,
        word_count: int,
        frequencies: list[tuple[str, int]],
    ) -> None:
        """Store analysis for one article and mark it processed.

        UA: Зберігає аналіз однієї статті та позначає її обробленою.
        """
        article.cleaned_content = cleaned_content
        article.processed = True
        article.analysis_results.append(
            AnalysisResult(
                sentiment_label=sentiment_label,
                sentiment_score=sentiment_score,
                topic=topic,
                word_count=word_count,
            )
        )
        for word, count in frequencies:
            article.word_frequencies.append(WordFrequency(word=word, count=count))
        self.session.commit()
