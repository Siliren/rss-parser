# Dependencies — what each package is for

> **UA:** Що робить кожен пакет і навіщо він у проєкті.
>
> Every package we install, why it's here, and which stage introduced it.
> **Where they're declared:** `requirements-core.txt` (minimal) and
> `requirements.txt` (full). spaCy + the language model are installed by hand
> (Stage 5) because the model is a large download.

## How install is split

| File / command | What it gives you | When |
|----------------|-------------------|------|
| `pip install -r requirements-core.txt` | API + DB + tests (run the app) | Stage 1 |
| `pip install -r requirements.txt` | + scraping, migrations, dashboard | Stage 3 / 10 |
| `pip install "spacy>=3.8.9"` + `python -m spacy download uk_core_news_sm` | Ukrainian NLP | Stage 5 |

> Tip: see exactly what's installed with `pip freeze`, or one package with
> `pip show <name>`.

## Direct packages (the ones we chose)

### Core — `requirements-core.txt`

| Package | What it does | Used in | Stage |
|---------|--------------|---------|-------|
| `fastapi` | Web framework for the REST API | `app/main.py`, `app/api/` | 1, 9 |
| `uvicorn[standard]` | ASGI server that runs FastAPI (`uvicorn app.main:app`) | run/deploy | 1 |
| `pydantic-settings` | Loads config from `.env` into a typed `Settings` | `app/config/settings.py` | 1 |
| `sqlalchemy` | ORM — defines tables, runs queries (SQLite) | `app/database/` | 2 |
| `httpx` | HTTP client for fetching news feeds | `app/collectors/base.py` | 3 |
| `pytest` | Test runner | `tests/` | 1+ |

### Full stack — `requirements.txt` (adds to core)

| Package | What it does | Used in | Stage |
|---------|--------------|---------|-------|
| `beautifulsoup4` | Parses HTML/XML (reads RSS items, strips HTML) | collectors, `cleaner.py` | 3, 5 |
| `lxml` | Fast XML parser backend BeautifulSoup uses for RSS (`"xml"`) | collectors | 3 |
| `trafilatura` | Extracts the main article body from a web page's HTML | `url_analysis_service.py` | URL feature |
| `lxml_html_clean` | Required by trafilatura/justext with lxml 5+ | (transitive use) | URL feature |
| `alembic` | Database migrations (schema changes over time) | — (set up later) | (later) |
| `streamlit` | Dashboard UI | `dashboard/` | 10 |
| `matplotlib` | Charts (sentiment, frequencies) | dashboard | 10 |
| `wordcloud` | Word-cloud image from word frequencies | dashboard | 10 |
| `pandas` | Tabular data for the dashboard | dashboard | 10 |

### NLP — installed by hand (Stage 5)

| Package | What it does | Used in | Stage |
|---------|--------------|---------|-------|
| `spacy` | NLP toolkit: tokenize, lemmatize, stopwords | `app/preprocessing/` | 5 |
| `uk_core_news_sm` | spaCy's Ukrainian model (the actual language data) | `lemmatizer.py` | 5 |

## Notable automatic dependencies (pulled in for you)

You don't list these — they come with the packages above. Good to recognize:

| Package | Comes with | Why it exists |
|---------|-----------|---------------|
| `pymorphy3` + `pymorphy3-dicts-uk` / `-ru` | `uk_core_news_sm` | Morphology engine + dictionaries the Ukrainian lemmatizer relies on |
| `starlette` | `fastapi` | The ASGI foundation FastAPI is built on |
| `pydantic` / `pydantic-core` | `fastapi`, `pydantic-settings` | Data validation / settings models |
| `soupsieve` | `beautifulsoup4` | CSS-selector support for BeautifulSoup |
| `anyio`, `h11`, `httpcore`, `certifi` | `httpx` | Async + HTTP/TLS plumbing |

## Deliberately NOT used

Django, Celery, GPT/LLM APIs — out of scope to keep the project small and
local. (See `docs/PROJECT_PLAN.md`.)
