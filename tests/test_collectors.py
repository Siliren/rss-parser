"""Tests for the news collectors (Stage 3).

UA: Тести збирачів новин.

We parse a static RSS sample so tests never hit the live network.
"""

from app.collectors import RawArticle, UkrinformCollector, UnianCollector

SAMPLE_RSS = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
  <channel>
    <title>Укрінформ</title>
    <item>
      <title>Перша новина</title>
      <link>https://www.ukrinform.ua/news/1/</link>
      <description>Короткий опис першої новини.</description>
      <pubDate>Sun, 28 Jun 2026 10:00:00 +0300</pubDate>
    </item>
    <item>
      <title>Друга новина</title>
      <link>https://www.ukrinform.ua/news/2/</link>
      <description>Опис другої.</description>
    </item>
  </channel>
</rss>"""


def test_parse_returns_raw_articles():
    """Each <item> becomes one RawArticle. / Кожен <item> → один RawArticle."""
    articles = UkrinformCollector().parse(SAMPLE_RSS)

    assert len(articles) == 2
    assert all(isinstance(a, RawArticle) for a in articles)


def test_parse_extracts_fields():
    """Title, url, content and date are read correctly. / Поля зчитуються вірно."""
    first = UkrinformCollector().parse(SAMPLE_RSS)[0]

    assert first.title == "Перша новина"
    assert first.url == "https://www.ukrinform.ua/news/1/"
    assert first.raw_content == "Короткий опис першої новини."
    assert first.published_at is not None
    assert first.published_at.year == 2026


def test_missing_pubdate_is_none():
    """An item without pubDate gets published_at=None. / Без дати → None."""
    second = UkrinformCollector().parse(SAMPLE_RSS)[1]

    assert second.published_at is None


def test_unian_shares_rss_parsing():
    """Second collector inherits the same parser. / Другий збирач — той самий парсер."""
    articles = UnianCollector().parse(SAMPLE_RSS)

    assert len(articles) == 2
    assert articles[0].title == "Перша новина"


def test_base_url_derived_from_feed_url():
    """base_url is the site root from feed_url. / base_url — корінь сайту."""
    assert UkrinformCollector().base_url == "https://www.ukrinform.ua"
    assert UnianCollector().base_url == "https://rss.unian.net"
