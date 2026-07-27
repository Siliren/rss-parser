"""Collectors package — one subclass of BaseCollector per news source."""

from app.collectors.base import BaseCollector, RawArticle
from app.collectors.rss import RssCollector
from app.collectors.ukrinform import UkrinformCollector
from app.collectors.unian import UnianCollector

__all__ = [
    "BaseCollector",
    "RawArticle",
    "RssCollector",
    "UkrinformCollector",
    "UnianCollector",
]
