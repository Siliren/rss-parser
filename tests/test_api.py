"""Tests for the FastAPI endpoints (Stage 9).

UA: Тести ендпоінтів FastAPI.

Uses an in-memory database via a dependency override, seeded through the
repository (no spaCy model needed for /articles and /analytics).
"""

import pytest
import spacy.util
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.collectors.base import BaseCollector, RawArticle
from app.database.base import Base
from app.database.repositories import ArticleRepository
from app.database.session import get_db
from app.main import app
from app.preprocessing.lemmatizer import MODEL_NAME

needs_model = pytest.mark.skipif(
    not spacy.util.is_package(MODEL_NAME),
    reason=f"{MODEL_NAME} not installed",
)


def _seed(db) -> None:
    """Put one analyzed article in the DB. / Додає одну проаналізовану статтю."""
    repo = ArticleRepository(db)
    source = repo.get_or_create_source("Тест", "https://t.example")
    articles = repo.save_articles(
        source,
        [RawArticle(url="https://t.example/1", title="Армія", raw_content="фронт")],
    )
    repo.save_analysis(
        articles[0],
        cleaned_content="армія фронт",
        sentiment_label="negative",
        sentiment_score=-0.5,
        topic="війна",
        word_count=2,
        frequencies=[("армія", 2), ("фронт", 1)],
    )


@pytest.fixture()
def client():
    """TestClient backed by a seeded in-memory DB. / Клієнт із засіяною БД."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestingSession() as db:
        _seed(db)

    yield TestClient(app)
    app.dependency_overrides.clear()


def test_list_articles(client):
    """GET /articles returns the seeded article with analysis. / Список статей."""
    response = client.get("/articles")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Армія"
    assert data[0]["source"] == "Тест"
    assert data[0]["topic"] == "війна"
    assert data[0]["sentiment_label"] == "negative"


def test_list_articles_filter_by_unknown_source(client):
    """Filtering by a missing source gives an empty list. / Порожній результат."""
    response = client.get("/articles", params={"source_id": 999})
    assert response.status_code == 200
    assert response.json() == []


def test_analytics(client):
    """GET /analytics aggregates counts, sentiment, topics, words. / Аналітика."""
    data = client.get("/analytics").json()

    assert data["total_articles"] == 1
    assert data["processed_articles"] == 1
    assert data["sentiment"] == {"negative": 1}
    assert {"name": "війна", "count": 1} in data["topics"]
    assert {"name": "армія", "count": 2} in data["top_words"]


def test_collect_invalid_source_returns_422(client):
    """Unknown source name is rejected by validation. / Невідоме джерело → 422."""
    assert client.post("/collect/bbc").status_code == 422


@needs_model
def test_collect_runs_pipeline(client, monkeypatch):
    """POST /collect/{source} runs the pipeline with a fake collector. / Збір."""
    from app.api.routers import collect as collect_router

    class FakeCollector(BaseCollector):
        source_name = "Укрінформ"
        feed_url = "https://www.ukrinform.ua/rss"

        def __init__(self) -> None:
            super().__init__(delay_seconds=0)

        def collect(self) -> list[RawArticle]:
            return [
                RawArticle(
                    url="https://www.ukrinform.ua/x",
                    title="Президент підписав закон",
                    raw_content="Парламент і уряд ухвалили рішення.",
                )
            ]

        def parse(self, content: str) -> list[RawArticle]:
            return []

    monkeypatch.setitem(
        collect_router.COLLECTORS,
        collect_router.SourceName.ukrinform,
        FakeCollector,
    )

    data = client.post("/collect/ukrinform").json()
    assert data["source"] == "Укрінформ"
    assert data["fetched"] == 1
    assert data["saved"] == 1
    assert data["processed"] == 1
