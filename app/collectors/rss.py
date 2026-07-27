"""Shared RSS collector — parses a standard RSS 2.0 feed.

UA: Спільний збирач RSS: розбирає стандартну стрічку RSS 2.0.

Most Ukrainian news sites expose the same RSS shape (title, link, description,
pubDate). A source-specific collector just subclasses this and sets
`source_name` + `feed_url` — no parsing code needed.
"""

from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup

from app.collectors.base import BaseCollector, RawArticle


class RssCollector(BaseCollector):
    """Parses RSS `<item>` tags into RawArticle objects.

    UA: Перетворює теги RSS `<item>` на обʼєкти RawArticle.
    """

    def parse(self, content: str) -> list[RawArticle]:
        """Read every RSS `<item>` into a RawArticle.

        UA: Зчитує кожен тег RSS `<item>` у RawArticle.
        """
        soup = BeautifulSoup(content, "xml")
        articles: list[RawArticle] = []

        for item in soup.find_all("item"):
            link = item.find("link")
            title = item.find("title")
            if link is None or title is None:
                continue  # skip malformed items / пропускаємо некоректні записи

            description = item.find("description")
            pub_date = item.find("pubDate")
            articles.append(
                RawArticle(
                    url=link.get_text(strip=True),
                    title=title.get_text(strip=True),
                    raw_content=description.get_text(strip=True) if description else "",
                    published_at=_parse_rss_date(
                        pub_date.get_text(strip=True) if pub_date else None
                    ),
                )
            )

        return articles


def _parse_rss_date(value: str | None) -> datetime | None:
    """Parse an RFC-822 RSS date, or return None if missing/invalid.

    UA: Розбирає дату RSS (RFC-822); повертає None, якщо немає чи помилка.
    """
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
