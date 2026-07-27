"""Tests for the analyze-a-URL service and endpoint (stateless).

UA: Тести сервісу та ендпоінта аналізу за URL.

`analyze_html` needs the spaCy model (skips if absent). The endpoint happy path
monkeypatches the service so it needs neither network nor model.
"""

import httpx
import pytest
import spacy.util
from fastapi.testclient import TestClient

from app.main import app
from app.preprocessing.lemmatizer import MODEL_NAME
from app.services import UrlAnalysis

needs_model = pytest.mark.skipif(
    not spacy.util.is_package(MODEL_NAME),
    reason=f"{MODEL_NAME} not installed",
)

SAMPLE_HTML = """
<html><head><title>Тестова стаття</title></head>
<body>
  <nav>Меню сайту</nav>
  <article>
    <h1>Армія звільнила місто</h1>
    <p>Війна триває: обстріл, оборона і фронт. Перемога близько.</p>
    <p>Президент відвідав регіон та подякував військовим.</p>
  </article>
  <footer>Підвал сайту</footer>
</body></html>
"""

client = TestClient(app)


@needs_model
def test_analyze_html_extracts_and_analyzes():
    """Pulls article text, returns sentiment/topic/words. / Аналіз HTML."""
    from app.services.url_analysis_service import analyze_html

    result = analyze_html("https://news.example/a", SAMPLE_HTML)
    # trafilatura returns the article headline (<h1>), not the <title> tag.
    assert result.title == "Армія звільнила місто"
    assert result.word_count > 0
    assert result.topic in {"війна", "політика", "інше"}
    assert len(result.top_words) > 0
    # boilerplate (nav/footer) is excluded by trafilatura
    assert "меню" not in [w for w, _ in result.top_words]


def test_endpoint_rejects_unsafe_url():
    """POST /analyze with a private URL → 400. / Небезпечний URL → 400."""
    response = client.post("/analyze", json={"url": "http://127.0.0.1/"})
    assert response.status_code == 400


def test_endpoint_happy_path(monkeypatch):
    """POST /analyze returns the service result, no network/model. / Щасливий шлях."""
    from app.api.routers import analyze as analyze_router

    def fake_analyze_url(url: str, **_) -> UrlAnalysis:
        return UrlAnalysis(
            url=url,
            title="Заголовок",
            word_count=12,
            sentiment_label="negative",
            sentiment_score=-0.5,
            topic="війна",
            top_words=[("армія", 3), ("фронт", 2)],
        )

    monkeypatch.setattr(analyze_router, "analyze_url", fake_analyze_url)

    data = client.post("/analyze", json={"url": "https://news.example/x"}).json()
    assert data["title"] == "Заголовок"
    assert data["topic"] == "війна"
    assert data["sentiment_label"] == "negative"
    assert {"name": "армія", "count": 3} in data["top_words"]
