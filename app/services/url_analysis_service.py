"""Analyze any article URL on demand — stateless (nothing saved to the DB).

UA: Аналіз будь-якої статті за URL на вимогу — без збереження в БД.

Reuses the existing preprocessing + analysis. The URL is validated first
(see url_safety) to avoid SSRF, then the main article text is extracted with
trafilatura and analyzed like a normal article.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import httpx
import trafilatura

from app.analysis import analyze_sentiment, detect_topic, word_frequencies
from app.config.settings import settings
from app.preprocessing import clean_text, lemmatize
from app.utils.url_safety import validate_url


@dataclass(frozen=True, slots=True)
class UrlAnalysis:
    """Analysis of one ad-hoc URL. / Аналіз одного довільного URL."""

    url: str
    title: str | None
    word_count: int
    sentiment_label: str
    sentiment_score: float
    topic: str
    top_words: list[tuple[str, int]]


def analyze_url(url: str, *, top_words_n: int = 20) -> UrlAnalysis:
    """Validate, fetch and analyze an article URL.

    UA: Перевіряє, завантажує та аналізує статтю за URL.
    """
    safe_url = validate_url(url)
    html = _fetch_html(safe_url)
    return analyze_html(safe_url, html, top_words_n=top_words_n)


def analyze_html(url: str, html: str, *, top_words_n: int = 20) -> UrlAnalysis:
    """Analyze already-fetched HTML (split out so it is testable offline).

    UA: Аналізує вже завантажений HTML (винесено окремо для тестів без мережі).
    """
    text, title = _extract(html)
    lemmas = lemmatize(text)
    sentiment = analyze_sentiment(lemmas)
    return UrlAnalysis(
        url=url,
        title=title,
        word_count=len(lemmas),
        sentiment_label=sentiment.label,
        sentiment_score=sentiment.score,
        topic=detect_topic(lemmas),
        top_words=word_frequencies(lemmas, top_words_n),
    )


def _extract(html: str) -> tuple[str, str | None]:
    """Pull the main article text + title from raw HTML.

    UA: Дістає основний текст статті та заголовок із сирого HTML.

    Falls back to a plain HTML strip if trafilatura finds nothing.
    """
    payload = trafilatura.extract(html, output_format="json", with_metadata=True)
    if payload:
        data = json.loads(payload)
        text = data.get("text") or ""
        if text:
            return text, data.get("title")
    return clean_text(html), None


def _fetch_html(url: str, *, timeout: float = 20.0) -> str:
    """Download a page politely (User-Agent, timeout, follow redirects).

    UA: Ввічливо завантажує сторінку (User-Agent, тайм-аут, редіректи).
    """
    with httpx.Client(
        headers={"User-Agent": settings.user_agent},
        timeout=timeout,
        follow_redirects=True,
    ) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text
