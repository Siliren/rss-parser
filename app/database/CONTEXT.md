# Context — `app/database/`

> **UA:** Шар бази даних: моделі, сесія, створення таблиць.
>
> The database layer: ORM models, the session/engine, and table creation.

## Purpose

Define *what* we store and *how* we connect to SQLite. Nothing here scrapes or
analyzes — it only describes tables and hands out sessions.

## Key files

| File | What it does |
|------|--------------|
| `base.py` | `Base` declarative class. Every model inherits from it. |
| `session.py` | `engine`, `SessionLocal`, `get_db()` (FastAPI dep), `init_db()`. |
| `models/source.py` | `Source` — a news site / Telegram channel. |
| `models/article.py` | `Article` — one collected item; unique by `url`. |
| `models/analysis.py` | `AnalysisResult` + `WordFrequency` — NLP output. |
| `models/__init__.py` | Imports all models so `init_db()` sees every table. |
| `repositories/` | (empty until Stage 4 — save/query helpers go here.) |

## Schema

```
sources (1) ──< articles (1) ──< analysis_results
                          └──< word_frequencies
```

- **Source**: `name` (unique), `base_url`, `type`, `active`, `created_at`.
- **Article**: `source_id` (FK), `url` (unique → dedup), `title`,
  `raw_content`, `cleaned_content`, `published_at`, `collected_at`, `processed`.
- **AnalysisResult**: `article_id` (FK), `sentiment_label`, `sentiment_score`,
  `topic`, `word_count`, `created_at`.
- **WordFrequency**: `article_id` (FK), `word`, `count`.

## Design decisions

- `base.py` is split from `session.py` so models import `Base` without pulling
  in the engine (no import cycles).
- Raw vs cleaned text are **separate columns** — we keep the original.
- Dedup is enforced by a DB-level `unique` constraint on `Article.url`.
- Relationships use `cascade="all, delete-orphan"`: deleting an article removes
  its analysis rows.

## How to use it

```bash
python -m scripts.init_db        # create data/media_nlp.db + tables
```

```python
from app.database.session import get_db, SessionLocal
from app.database.models import Source, Article
```

## Tested by

`tests/test_models.py` — relationships, unique-URL dedup, analysis attachment
(runs on in-memory SQLite, never touches the real DB file).

## Next that touches this layer

Stage 4 — add an article repository in `repositories/` (`save_article`,
`get_articles`, dedup by URL).
