"""Tests for the PipelineService (Stage 7).

UA: Тести PipelineService.

Uses a fake collector (no network) and in-memory SQLite. The analysis step
needs the spaCy model, so these tests skip if it is not installed.
"""

import pytest
import spacy.util
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.collectors.base import BaseCollector, RawArticle
from app.database.base import Base
from app.database.repositories import ArticleRepository
from app.preprocessing.lemmatizer import MODEL_NAME
from app.services import PipelineService

needs_model = pytest.mark.skipif(
    not spacy.util.is_package(MODEL_NAME),
    reason=f"{MODEL_NAME} not installed",
)


class FakeCollector(BaseCollector):
    """Returns canned articles instead of hitting the network. / Без мережі."""

    source_name = "Тест"
    feed_url = "https://test.example/rss"

    def __init__(self, articles: list[RawArticle]) -> None:
        super().__init__(delay_seconds=0)
        self._articles = articles

    def collect(self) -> list[RawArticle]:
        return self._articles

    def parse(self, content: str) -> list[RawArticle]:  # not used in tests
        return []


@pytest.fixture()
def session():
    """Fresh in-memory database. / Нова БД у памʼяті."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    db: Session = sessionmaker(bind=engine)()
    try:
        yield db
    finally:
        db.close()


SAMPLE = [
    RawArticle(
        url="https://test.example/1",
        title="Армія звільнила місто",
        raw_content="Війна триває: обстріл, оборона і фронт. Перемога близько.",
    ),
    RawArticle(
        url="https://test.example/2",
        title="Президент підписав закон",
        raw_content="Парламент і уряд ухвалили рішення про вибори.",
    ),
]


@needs_model
def test_pipeline_runs_end_to_end(session):
    """collect → save → analyze; report counts match. / Наскрізний прогін."""
    report = PipelineService(session, FakeCollector(SAMPLE)).run()

    assert report.fetched == 2
    assert report.saved == 2
    assert report.processed == 2


@needs_model
def test_pipeline_writes_analysis_to_db(session):
    """Each article gets cleaned text, analysis and frequencies. / Запис у БД."""
    PipelineService(session, FakeCollector(SAMPLE)).run()

    article = ArticleRepository(session).get_articles()[0]
    assert article.processed is True
    assert article.cleaned_content
    assert len(article.analysis_results) == 1
    assert article.analysis_results[0].topic in {"війна", "політика", "інше"}
    assert len(article.word_frequencies) > 0


@needs_model
def test_pipeline_is_idempotent(session):
    """Re-running saves and processes nothing new. / Повторний запуск — без новин."""
    collector = FakeCollector(SAMPLE)
    PipelineService(session, collector).run()
    second = PipelineService(session, collector).run()

    assert second.saved == 0
    assert second.processed == 0
