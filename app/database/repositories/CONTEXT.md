# Context — `app/database/repositories/`

> **UA:** Репозиторії: єдине місце доступу до БД для статей.
>
> Repositories are the only place that reads/writes articles in the database.
> Collectors produce data; repositories persist it.
> **Status:** Stage 4 ✅ done.

## Purpose

Keep all article SQL in one small, testable place. Collectors and (later)
services call the repository instead of writing queries themselves.

## Key files

| File | What it does |
|------|--------------|
| `article_repository.py` | `ArticleRepository` — save & read articles. |
| `__init__.py` | Exports `ArticleRepository`. |

## API

```python
from app.database.session import SessionLocal
from app.database.repositories import ArticleRepository

with SessionLocal() as db:
    repo = ArticleRepository(db)
    source = repo.get_or_create_source("Укрінформ", "https://www.ukrinform.ua")
    new = repo.save_articles(source, raw_articles)   # list[RawArticle] -> list[Article]
    recent = repo.get_articles(source_id=source.id, limit=50)
```

- `get_or_create_source(name, base_url, source_type="news")` — reuse by `name`,
  create if missing.
- `save_articles(source, raw_articles)` — insert new ones, **skip URLs already
  stored and duplicates within the batch**; returns only the new articles.
- `get_articles(source_id=None, limit=50)` — newest first, optional source filter.
- `get_unprocessed_articles(limit=None)` — articles with `processed=False` (Stage 7).
- `save_analysis(article, ...)` — store `cleaned_content`, an `AnalysisResult`
  and `WordFrequency` rows, set `processed=True` (Stage 7).

## Design decisions

- **Dedup by `url`**: one batched query fetches which incoming URLs already
  exist, plus an in-batch `seen` set — so re-running a collector saves 0.
- The repository **commits** for simplicity (educational project). A future
  service could take over transaction control if needed.
- Takes a `Session` in the constructor → easy to test with in-memory SQLite.

## Tested by

`tests/test_repository.py` — source idempotency, insert, dedup (existing +
in-batch), source filtering. Verified live: 30 fetched → 30 saved → re-run 0.

## Next that touches this layer

Stage 5 fills `cleaned_content`; Stage 7's `PipelineService` will call
`save_articles` then hand new articles to preprocessing/analysis.
