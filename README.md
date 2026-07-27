**Pipeline:** News RSS → Collectors → Preprocessing → Analysis → SQLite →
FastAPI / Streamlit

The full data flow runs end to end: **collect → save (dedup) → preprocess →
analyze → store → visualize**, exposed via a REST API and a Streamlit dashboard.

## Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.10+ (developed on 3.10; 3.12+ fine) |
| Scraping | httpx + BeautifulSoup4 (RSS) + lxml |
| URL extraction | trafilatura (main-article text from any page) |
| NLP | spaCy (`uk_core_news_sm`) |
| Database | SQLite (dev) — swappable to Postgres via `DATABASE_URL` |
| ORM | SQLAlchemy 2.0 |
| API | FastAPI |
| Dashboard | Streamlit (UK/EN switcher) |
| Tests | pytest |

**Deliberately not used:** Django, Celery, GPT/LLM APIs.

## Quick start (Linux)

```bash
cd media-nlp-analyzer

# venv (Debian/Ubuntu may need: sudo apt install python3-venv)
python3 -m venv venv
source venv/bin/activate

# 1) minimal — run the API + tests
pip install -r requirements-core.txt

# 2) full stack — scraping, URL analysis, dashboard
pip install -r requirements.txt

# 3) NLP model (one large download, needed for preprocessing/analysis)
python -m spacy download uk_core_news_sm

# config
cp .env.example .env
```

> Windows: use `py -3 -m venv venv` and `venv\Scripts\activate`; everything else
> is the same.

## Run

```bash
# 1) Create the database tables
python -m scripts.init_db

# 2) Collect + analyze the latest news (collect → save → preprocess → analyze)
python -m scripts.run_pipeline

# 3a) REST API  → http://127.0.0.1:8000/docs  (interactive Swagger UI)
uvicorn app.main:app --reload

# 3b) Dashboard → http://localhost:8501  (language switcher in the sidebar)
streamlit run dashboard/streamlit_app.py

# Tests (model-dependent tests skip automatically if the spaCy model is absent)
pytest
```

### API endpoints

| Method & path | Description |
|---------------|-------------|
| `GET /health` | Liveness probe |
| `GET /articles?source_id&limit` | Recent articles + their analysis |
| `GET /analytics?top_words` | Totals, sentiment, topic & word counts |
| `POST /collect/{source}` | Run the pipeline for `ukrinform` / `unian` |
| `POST /analyze` | Analyze any article URL (stateless, not stored) |

## Features

- **Two RSS collectors** (Ukrinform, UNIAN) via a shared `RssCollector`; adding a
  source is ~4 lines.
- **Preprocessing:** clean HTML → tokenize → drop Ukrainian stopwords → lemmatize.
- **Analysis:** word frequency, dictionary sentiment, keyword topic detection.
- **Analyze any URL:** paste a link → main-article text is extracted and analyzed
  on the fly (SSRF-guarded, nothing saved).
- **Dashboard i18n:** Ukrainian / English switcher (dictionary-based, no extra dep).

## Project structure

```
media-nlp-analyzer/
├── app/
│   ├── main.py                  # FastAPI app + router wiring
│   ├── config/settings.py       # .env config (DATABASE_URL, etc.)
│   ├── collectors/              # RSS collectors (base, rss, ukrinform, unian)
│   ├── preprocessing/           # cleaner, tokenizer, stopwords, lemmatizer
│   ├── analysis/                # frequency, sentiment, topic_detection
│   ├── services/                # PipelineService + analyze_url (stateless)
│   ├── database/
│   │   ├── models/              # Source, Article, AnalysisResult, WordFrequency
│   │   ├── repositories/        # ArticleRepository, AnalyticsRepository
│   │   ├── base.py, session.py  # Base, engine, get_db, init_db
│   ├── api/routers/             # articles, analytics, collect, analyze
│   ├── schemas/                 # Pydantic response DTOs
│   └── utils/url_safety.py      # SSRF guard for analyze-a-URL
├── dashboard/
│   ├── streamlit_app.py         # UI
│   └── i18n.py                  # translations + language switcher
├── scripts/                     # init_db, run_pipeline (CLI)
├── tests/                       # pytest (48 tests)
├── docs/                        # see "Documentation" below
└── data/                        # SQLite DB (gitignored)
```

Most folders under `app/` also contain a `CONTEXT.md` describing that module.

## Documentation

Read these to get oriented fast — you rarely need to read all the code:

| Doc | What it's for |
|-----|---------------|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | One-page map of the whole project; start here |
| [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md) | Roadmap, current stage, session log |
| [`docs/DEPENDENCIES.md`](docs/DEPENDENCIES.md) | What every package is for |
| [`docs/DEPLOY.md`](docs/DEPLOY.md) | Cheap/free hosting recipe (Streamlit Cloud + free Postgres) |
| `app/**/CONTEXT.md` | Per-module purpose, key files, design decisions |

## Conventions

- Python 3.10+ type hints; SQLAlchemy 2.0 declarative style.
- Main classes/functions have a one-line English docstring + a short `UA:` line.
- Layers stay separate: collectors don't do NLP; analysis is pure functions;
  repositories own all DB access; routers are thin.
- Each module gets a `CONTEXT.md`; update `docs/PROJECT_PLAN.md` after each stage.

## For an AI assistant / new contributor

Starting a fresh session? Say:

> Read `docs/ARCHITECTURE.md` and `docs/PROJECT_PLAN.md`, then continue from the
> current stage.

Rules: no Django / Celery / LLM APIs; keep it simple and readable; build the
pipeline before the UI; update `PROJECT_PLAN.md` (and the relevant `CONTEXT.md`)
when you finish a stage.
