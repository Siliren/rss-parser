# Context — `app/collectors/`

> **UA:** Збирачі новин: завантажують RSS і повертають «сирі» статті.
>
> Collectors fetch a news source and return raw articles. They do **not** touch
> the database or do any NLP — that keeps each one tiny.
> **Status:** Stage 3 ✅ (Ukrinform) + Stage 8 ✅ (UNIAN, 2 sources total).

## Purpose

Get fresh articles from a source into plain `RawArticle` objects. One subclass
per source (adapter pattern), so adding a source = a few lines.

## Key files

| File | What it does |
|------|--------------|
| `base.py` | `RawArticle` dataclass + `BaseCollector` (polite HTTP, `base_url`, `parse()` interface). |
| `rss.py` | `RssCollector` — shared RSS 2.0 parsing (title/link/description/pubDate). |
| `ukrinform.py` | `UkrinformCollector(RssCollector)` — just name + feed_url. |
| `unian.py` | `UnianCollector(RssCollector)` — just name + feed_url. |
| `__init__.py` | Exports the base classes + both collectors. |

## How it works

```python
from app.collectors import UkrinformCollector

articles = UkrinformCollector().collect()   # list[RawArticle]
```

- `collect()` → `_fetch(feed_url)` (sets User-Agent, waits `SCRAPE_DELAY_SECONDS`,
  raises on HTTP error) → `parse(content)`.
- `parse()` reads RSS `<item>` tags (BeautifulSoup, `xml` parser via lxml) into
  `RawArticle(url, title, raw_content, published_at)`.

## Adding a new source

If it's a standard RSS feed (most are), it's tiny:

```python
from app.collectors.rss import RssCollector

class MySourceCollector(RssCollector):
    source_name = "Назва"
    feed_url = "https://example.com/rss"
```

1. New file `app/collectors/<name>.py` (subclass `RssCollector`, set the two
   attributes — no parsing code).
2. Export it from `__init__.py`.
3. If the feed is non-standard, subclass `BaseCollector` instead and write `parse()`.

## Design decisions

- **RSS, not HTML scraping** — stable structure, polite, easy to parse.
- Collectors return data only; saving (dedup by URL) is the repository's job
  (Stage 4), analysis is Stage 6.
- HTTP lives only in `BaseCollector._fetch`; subclasses are pure parsing — easy
  to unit-test without network.

## Tested by

`tests/test_collectors.py` — parses a static RSS sample (no live network):
item count, field extraction, missing-date handling.

## Notes / gotchas

- The `xml` parser needs **lxml** (in `requirements.txt`).
- **pravda.com.ua is blocked** by Cloudflare (403) even with a browser UA — we
  did not bypass it. Ukrinform/UNIAN/Suspilne serve RSS to our own User-Agent.
- Full article body isn't fetched yet — `raw_content` is the RSS summary. Fetching
  full text per link can come later if needed.

## Next that touches this layer

Stage 4 — repository saves `RawArticle`s into the DB (dedup by `url`).
Stage 8 — add a second collector (UNIAN or Suspilne, same RSS shape).
