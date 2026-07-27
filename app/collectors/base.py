"""Base collector — shared HTTP plus the collector interface.

UA: Базовий збирач: спільний HTTP-клієнт та інтерфейс для збирачів.

Each news source gets its own subclass (adapter pattern). The base handles the
polite HTTP request; subclasses only implement `parse()`.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlsplit

import httpx

from app.config.settings import settings


@dataclass(frozen=True, slots=True)
class RawArticle:
    """One article as collected, before cleaning or DB storage.

    UA: Одна зібрана стаття до очищення та збереження в БД.
    """

    url: str
    title: str
    raw_content: str
    published_at: datetime | None = None


class BaseCollector(ABC):
    """Common base for all source collectors (adapter pattern).

    UA: Спільна основа для всіх збирачів джерел (патерн «адаптер»).

    Subclasses set `source_name` + `feed_url` and implement `parse()`.
    """

    source_name: str  # stored later as Source.name
    feed_url: str  # feed / listing URL to fetch

    def __init__(self, *, delay_seconds: int | None = None) -> None:
        self.delay_seconds = (
            settings.scrape_delay_seconds if delay_seconds is None else delay_seconds
        )
        self.headers = {"User-Agent": settings.user_agent}

    @property
    def base_url(self) -> str:
        """Site root derived from `feed_url` (e.g. https://www.ukrinform.ua).

        UA: Корінь сайту, похідний від `feed_url`.
        """
        parts = urlsplit(self.feed_url)
        return f"{parts.scheme}://{parts.netloc}"

    def collect(self) -> list[RawArticle]:
        """Fetch the feed and return parsed raw articles.

        UA: Завантажує стрічку й повертає розібрані статті.
        """
        content = self._fetch(self.feed_url)
        return self.parse(content)

    def _fetch(self, url: str) -> str:
        """Polite GET: wait, set User-Agent, return the response text.

        UA: Ввічливий GET: пауза, User-Agent, повертає текст відповіді.
        """
        time.sleep(self.delay_seconds)
        response = httpx.get(
            url, headers=self.headers, timeout=20.0, follow_redirects=True
        )
        response.raise_for_status()
        return response.text

    @abstractmethod
    def parse(self, content: str) -> list[RawArticle]:
        """Turn fetched content into RawArticle objects.

        UA: Перетворює завантажений вміст на обʼєкти RawArticle.
        """
        raise NotImplementedError
