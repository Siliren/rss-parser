"""Collector for Ukrinform via its RSS feed.

UA: Збирач для «Укрінформ» через стрічку RSS.

Ukrinform serves its feed to our own User-Agent, so no browser tricks are needed.
All parsing is inherited from RssCollector.
"""

from __future__ import annotations

from app.collectors.rss import RssCollector


class UkrinformCollector(RssCollector):
    """Collects latest items from Ukrinform's RSS feed.

    UA: Збирає останні новини зі стрічки RSS «Укрінформ».
    """

    source_name = "Укрінформ"
    feed_url = "https://www.ukrinform.ua/rss/block-lastnews"
