"""PipelineService — runs the whole flow end to end.

UA: PipelineService — виконує весь процес від початку до кінця.

collect → save (dedup) → preprocess → analyze → store results.
This is the one place that ties collectors, repository, preprocessing and
analysis together.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.analysis import analyze_sentiment, detect_topic, word_frequencies
from app.collectors.base import BaseCollector
from app.database.models import Article
from app.database.repositories import ArticleRepository
from app.preprocessing import clean_text, lemmatize


@dataclass(frozen=True, slots=True)
class PipelineReport:
    """What one pipeline run did. / Підсумок одного запуску конвеєра."""

    fetched: int  # articles returned by the collector
    saved: int  # new articles stored (after dedup)
    processed: int  # articles analyzed this run


class PipelineService:
    """Collect, store and analyze articles for one source.

    UA: Збирає, зберігає та аналізує статті одного джерела.
    """

    def __init__(
        self,
        session: Session,
        collector: BaseCollector,
        *,
        top_words: int = 20,
    ) -> None:
        self.repo = ArticleRepository(session)
        self.collector = collector
        self.top_words = top_words

    def run(self) -> PipelineReport:
        """Run the full pipeline once and return a short report.

        UA: Виконує весь конвеєр один раз і повертає короткий звіт.
        """
        raw_articles = self.collector.collect()
        source = self.repo.get_or_create_source(
            self.collector.source_name, self.collector.base_url
        )
        new_articles = self.repo.save_articles(source, raw_articles)

        processed = 0
        for article in self.repo.get_unprocessed_articles():
            self._analyze_article(article)
            processed += 1

        return PipelineReport(
            fetched=len(raw_articles),
            saved=len(new_articles),
            processed=processed,
        )

    def _analyze_article(self, article: Article) -> None:
        """Preprocess + analyze one article, then save the results.

        UA: Препроцесинг + аналіз однієї статті, далі зберігання результатів.
        """
        text = f"{article.title}. {article.raw_content or ''}"
        cleaned = clean_text(text)
        lemmas = lemmatize(cleaned)

        sentiment = analyze_sentiment(lemmas)
        self.repo.save_analysis(
            article,
            cleaned_content=cleaned,
            sentiment_label=sentiment.label,
            sentiment_score=sentiment.score,
            topic=detect_topic(lemmas),
            word_count=len(lemmas),
            frequencies=word_frequencies(lemmas, self.top_words),
        )
