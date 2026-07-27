"""Tests for the article repository (Stage 4).

UA: Тести репозиторію статей.

In-memory SQLite, so nothing touches the real data/ file.
"""

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.collectors.base import RawArticle
from app.database.base import Base
from app.database.repositories import ArticleRepository


@pytest.fixture()
def session():
    """Fresh in-memory database for each test. / Нова БД у памʼяті на кожен тест."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    db: Session = factory()
    try:
        yield db
    finally:
        db.close()


def _raw(n: int) -> RawArticle:
    """Helper: build a sample RawArticle. / Допоміжна: створює зразок RawArticle."""
    return RawArticle(
        url=f"https://news.example/{n}",
        title=f"Новина {n}",
        raw_content=f"Текст {n}",
        published_at=datetime(2026, 6, 28, 10, n % 60),
    )


def test_get_or_create_source_is_idempotent(session):
    """Same name returns the same row, no duplicates. / Без дублікатів джерел."""
    repo = ArticleRepository(session)
    first = repo.get_or_create_source("Укрінформ", "https://www.ukrinform.ua")
    second = repo.get_or_create_source("Укрінформ", "https://www.ukrinform.ua")

    assert first.id == second.id


def test_save_articles_inserts_new(session):
    """New articles are stored and returned. / Нові статті зберігаються."""
    repo = ArticleRepository(session)
    source = repo.get_or_create_source("Укрінформ", "https://www.ukrinform.ua")

    saved = repo.save_articles(source, [_raw(1), _raw(2)])

    assert len(saved) == 2
    assert all(a.id is not None for a in saved)


def test_save_articles_dedups_by_url(session):
    """Existing URLs and in-batch duplicates are skipped. / Дублікати пропускаються."""
    repo = ArticleRepository(session)
    source = repo.get_or_create_source("Укрінформ", "https://www.ukrinform.ua")
    repo.save_articles(source, [_raw(1)])

    # _raw(1) already stored; _raw(2) appears twice in this batch.
    saved = repo.save_articles(source, [_raw(1), _raw(2), _raw(2)])

    assert len(saved) == 1
    assert saved[0].url == "https://news.example/2"
    assert len(repo.get_articles()) == 2  # only 2 unique total


def test_get_articles_filters_by_source(session):
    """Filtering returns only that source's articles. / Фільтр за джерелом."""
    repo = ArticleRepository(session)
    src_a = repo.get_or_create_source("A", "https://a.example")
    src_b = repo.get_or_create_source("B", "https://b.example")
    repo.save_articles(src_a, [_raw(1), _raw(2)])
    repo.save_articles(src_b, [_raw(3)])

    assert len(repo.get_articles(source_id=src_a.id)) == 2
    assert len(repo.get_articles(source_id=src_b.id)) == 1
