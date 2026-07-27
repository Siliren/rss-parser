# Context — `app/api/`

> **UA:** HTTP-шар: тонкі ендпоінти поверх сервісів і репозиторіїв.
>
> The HTTP layer. Routers are **thin** — they call the repository/service and
> shape the result with Pydantic schemas. No business logic lives here.
> **Status:** Stage 9 ✅ done.

## Endpoints

| Method & path | What it does | Backed by |
|---------------|--------------|-----------|
| `GET /health` | Liveness probe | `app/main.py` |
| `GET /articles?source_id&limit` | Recent articles + their analysis | `ArticleRepository.get_articles` |
| `GET /analytics?top_words` | Totals, sentiment, topics, top words | `AnalyticsRepository` |
| `POST /collect/{source}` | Run the pipeline for `ukrinform`/`unian` | `PipelineService.run` |
| `POST /analyze` | Analyze any article URL (stateless, not saved) | `analyze_url` service |

Interactive docs while the server runs: **http://127.0.0.1:8000/docs**.

## Key files

| File | What it does |
|------|--------------|
| `routers/articles.py` | `GET /articles`; flattens Article + latest analysis into `ArticleOut`. |
| `routers/analytics.py` | `GET /analytics` via `AnalyticsRepository`. |
| `routers/collect.py` | `POST /collect/{source}`; `SourceName` enum → collector class. |
| `routers/analyze.py` | `POST /analyze`; validates URL (SSRF), calls `analyze_url`. |
| (schemas) | `app/schemas/` — `ArticleOut`, `AnalyticsOut`, `LabelCount`, `CollectResponse`, `UrlAnalysis*`. |

## How it fits

```
HTTP request
  → router (app/api/routers/*)          # thin: parse params, call down, shape output
    → repository / PipelineService       # all the real work
      → models / preprocessing / analysis
  → Pydantic schema (app/schemas/*)      # response shape
```

- DB session comes from the `get_db` dependency (`app/database/session.py`).
- The `source` path param is a `SourceName` enum, so FastAPI validates it
  automatically (unknown source → 422).

## Design decisions

- **Thin routers** (architecture rule 3): no SQL, no NLP here.
- `/collect` runs **synchronously** (fetch + spaCy), so it can take a few seconds.
  Acceptable for this project; could move to a background task later.
- Aggregation SQL lives in `AnalyticsRepository`, not in the router.

## Tested by

`tests/test_api.py` — in-memory DB via `get_db` dependency override; checks
`/articles`, `/analytics`, `/collect` validation (422), and a `/collect` happy
path with a fake collector (skips if the spaCy model is absent). Verified live
against the real DB (132 articles).

## Next that touches this layer

Stage 10 — the Streamlit dashboard reads the same repositories (or these
endpoints) to draw the article list, word cloud and sentiment chart.
