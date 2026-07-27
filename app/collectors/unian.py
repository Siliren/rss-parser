"""Collector for UNIAN via its RSS feed.

UA: Збирач для «УНІАН» через стрічку RSS.

Same RSS shape as Ukrinform, so parsing comes from RssCollector.
"""

from __future__ import annotations

from app.collectors.rss import RssCollector


class UnianCollector(RssCollector):
    """Collects latest items from UNIAN's RSS feed.

    UA: Збирає останні новини зі стрічки RSS «УНІАН».
    """

    source_name = "УНІАН"
    feed_url = "https://rss.unian.net/site/news_ukr.rss"
