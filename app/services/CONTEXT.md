# Context — `app/services/`

> **UA:** Сервіси: оркестратори, що поєднують усі кроки конвеєра.
>
> Services tie collectors, the repository, preprocessing and analysis together.
> This is the layer that actually *runs* the pipeline.
> **Status:** Stage 7 ✅ done.

## Purpose

One command that does the whole job: collect → save → preprocess → analyze →
store. Routers (Stage 9) and the scheduler (Stage 11) will just call this.

## Key files

| File | What it does |
|------|--------------|
| `pipeline_service.py` | `PipelineService` + `PipelineReport` — the curated-source pipeline. |
| `url_analysis_service.py` | `analyze_url(url)` — analyze ANY article URL on demand, **stateless** (nothing saved). |
| `__init__.py` | Exports all of the above. |

## analyze_url (the "paste a URL" feature)

```python
from app.services import analyze_url
result = analyze_url("https://www.ukrinform.ua/.../article.html")
# UrlAnalysis(title, topic, sentiment_label/score, word_count, top_words)
```

- **Stateless by design:** not saved to the DB (keeps the curated data clean and
  avoids unbounded growth from arbitrary input).
- **SSRF-guarded:** `app/utils/url_safety.validate_url` runs first — only public
  http(s) URLs; blocks localhost / private / link-local / metadata addresses.
- **Extraction:** `trafilatura` pulls the main article body (drops nav/ads/footer),
  far better than a raw HTML strip; falls back to `clean_text` if it finds nothing.
- `analyze_html(url, html)` is split out so it can be unit-tested offline.
- Known limitation: DNS-rebinding / redirect-to-internal is not fully closed
  (acceptable for this project's scope).

## Flow

```
collector.collect()                      # list[RawArticle]
repo.get_or_create_source(...)           # Source
repo.save_articles(source, raw)          # new articles only (dedup by url)
for each unprocessed article:
    clean_text -> lemmatize              # app.preprocessing
    analyze_sentiment / detect_topic / word_frequencies   # app.analysis
    repo.save_analysis(...)              # AnalysisResult + WordFrequency, processed=True
return PipelineReport(fetched, saved, processed)
```

## Usage

```python
from app.collectors import UkrinformCollector
from app.database.session import SessionLocal
from app.services import PipelineService

with SessionLocal() as db:
    report = PipelineService(db, UkrinformCollector()).run()
    # PipelineReport(fetched=30, saved=2, processed=32)
```

Or from the shell: `python -m scripts.run_pipeline`.

## Design decisions

- **Idempotent:** processes only `processed=False` articles and dedups by URL, so
  re-running is safe (second run = 0 saved, 0 processed).
- **Orchestration only:** all DB writes go through `ArticleRepository`
  (`save_articles`, `save_analysis`, `get_unprocessed_articles`); all NLP lives in
  `preprocessing` / `analysis`. The service just wires them in order.
- Works with any `BaseCollector` — pass a different collector to process another
  source (Stage 8).

## Tested by

`tests/test_pipeline.py` — end-to-end with a `FakeCollector` (no network),
verifies report counts, DB writes (cleaned text, analysis, frequencies) and
idempotency. Skips if the spaCy model is absent. Verified live: 30 fetched,
32 processed, re-run 0.

## Next that touches this layer

Stage 8 — second collector (the service already accepts any collector).
Stage 9 — FastAPI `/collect` endpoint calls `PipelineService.run()`.
