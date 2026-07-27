# Architecture — one-page map

> **UA:** Карта проєкту. Прочитай це, щоб зрозуміти структуру за 2 хвилини.
>
> Read this first to understand the whole structure in ~2 minutes.
> Each module folder also has its own `CONTEXT.md` with local details.

## The pipeline (data flow)

```
Source (news site)  →  Collector  →  Article (raw text)  →  Preprocessing
                                                                  ↓
        Streamlit / FastAPI  ←  AnalysisResult + WordFrequency  ←  Analysis
                              (all stored in SQLite via SQLAlchemy)
```

Each arrow is one responsibility. A module only knows about its own step —
collectors don't do NLP, analysis doesn't touch HTTP. This keeps every piece
small and easy to read.

## Where things live

| Folder | Responsibility | Stage | Context doc |
|--------|----------------|-------|-------------|
| `app/config/` | Settings from `.env` | 1 ✅ | — |
| `app/database/` | Models, session, `init_db` | 2 ✅ | `app/database/CONTEXT.md` |
| `app/collectors/` | Fetch news RSS → raw articles | 3 ✅, 8 ✅ | `app/collectors/CONTEXT.md` |
| `app/database/repositories/` | Save/query articles (dedup) | 4 ✅ | `app/database/repositories/CONTEXT.md` |
| `app/preprocessing/` | Clean, tokenize, lemmatize text | 5 ✅ | `app/preprocessing/CONTEXT.md` |
| `app/analysis/` | Frequency, sentiment, topics | 6 ✅ | `app/analysis/CONTEXT.md` |
| `app/services/` | PipelineService + analyze-a-URL (stateless) | 7 ✅ | `app/services/CONTEXT.md` |
| `app/utils/` | Shared helpers (URL safety / SSRF guard) | — | — |
| `app/api/` | FastAPI HTTP endpoints (thin) | 9 ✅ | `app/api/CONTEXT.md` |
| `app/schemas/` | Pydantic response DTOs | 9 ✅ | — |
| `dashboard/` | Streamlit UI | 10 ✅ | `dashboard/CONTEXT.md` |
| `scripts/` | CLI tools: `init_db`, `run_pipeline` | — | — |
| `tests/` | pytest | ongoing | — |

## How to read this project

1. Start here, then read `docs/PROJECT_PLAN.md` for the roadmap + current stage.
   For "what is this package for?" see `docs/DEPENDENCIES.md`; for hosting see
   `docs/DEPLOY.md`.
2. Opening a module? Read its `CONTEXT.md` before the code — it tells you the
   purpose, the key files, and the design decisions, so you rarely need to read
   every file.
3. Each `CONTEXT.md` follows the same short template (see `app/database/CONTEXT.md`).

## Conventions (kept deliberately simple)

- Python 3.10+ type hints (`Mapped[int]`, `str | None`).
- Main classes/functions have a one-line English docstring + a short `UA:` line.
- SQLAlchemy 2.0 declarative style (`Mapped` / `mapped_column`).
- No Django, no Celery, no GPT/LLM API.
