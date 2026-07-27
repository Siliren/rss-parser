"""Tests for the database models and their relationships (Stage 2).

UA: Тести моделей бази даних та звʼязків між ними.

Uses an in-memory SQLite database so nothing touches the real data/ file.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base
from app.database.models import AnalysisResult, Article, Source, WordFrequency


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


def test_source_to_article_relationship(session):
    """A source links to its articles both ways. / Звʼязок джерело ↔ статті."""
    source = Source(name="Example News", base_url="https://example.com")
    article = Article(url="https://example.com/a1", title="Привіт", source=source)
    session.add(source)
    session.commit()

    assert article.id is not None
    assert article.source.name == "Example News"
    assert source.articles[0].url == "https://example.com/a1"


def test_url_is_unique(session):
    """Duplicate URLs are rejected (dedup). / Дублікати URL відхиляються."""
    source = Source(name="S", base_url="https://s.com")
    session.add(source)
    session.commit()

    session.add(Article(url="https://s.com/x", title="A", source_id=source.id))
    session.commit()

    session.add(Article(url="https://s.com/x", title="B", source_id=source.id))
    with pytest.raises(IntegrityError):
        session.commit()


def test_analysis_and_word_frequency(session):
    """Analysis + word counts attach to an article. / Аналіз і частоти слів."""
    source = Source(name="S", base_url="https://s.com")
    article = Article(url="https://s.com/p", title="P", source=source)
    article.analysis_results.append(
        AnalysisResult(sentiment_label="positive", sentiment_score=0.8)
    )
    article.word_frequencies.append(WordFrequency(word="новини", count=5))
    session.add(source)
    session.commit()

    assert article.analysis_results[0].sentiment_label == "positive"
    assert article.word_frequencies[0].word == "новини"
