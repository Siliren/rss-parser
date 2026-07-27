# Deploy — the cheap / free way

> **UA:** Як задешево (безкоштовно) розгорнути проєкт.
>
> Goal: run this live for lots of readers without paying much (ideally $0).

## First: storage is NOT your cost problem

Each article is ~2.3 KB. Kept **forever**:

| Ingest | 10 years | Size |
|--------|----------|------|
| 30/day | ~110k articles | ~250 MB |
| 60/day | ~220k articles | ~500 MB |

That fits in the **free tier** of every managed database. So keep articles
forever — the thing to watch is **where the app runs** and **read traffic**, not
the database size.

## Recommended $0/month stack

```
GitHub Actions (cron)            Streamlit Community Cloud
   runs the pipeline      →      reads + shows the dashboard
        │                                  │
        └──────────  free Postgres  ───────┘
                  (Neon or Supabase)
```

| Piece | Service | Why | Notes |
|-------|---------|-----|-------|
| Dashboard | Streamlit Community Cloud | free, handles many readers | app sleeps when idle; ~1 GB RAM |
| Database | Neon **or** Supabase (Postgres) | free tier ≈ 0.5 GB = years of data | needed because Streamlit Cloud disk is **ephemeral** |
| Collection | GitHub Actions scheduled workflow | free, no always-on server | runs `scripts.run_pipeline` on a cron |

### Why move off SQLite for deploy?
Not size — **persistence**. Streamlit Community Cloud wipes the local disk on
every restart/redeploy, so a SQLite file would disappear. A managed Postgres
keeps the data between restarts.

## Switching SQLite → Postgres (one line, thanks to SQLAlchemy)

1. Create a free DB on Neon/Supabase, copy its connection string.
2. Add a Postgres driver to `requirements.txt`:
   ```
   psycopg2-binary>=2.9
   ```
3. Set the URL (locally in `.env`, on hosts via their secrets UI):
   ```
   DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME
   ```
4. Create the tables once against the new DB: `python -m scripts.init_db`.

No code changes — `app/config/settings.py` already reads `DATABASE_URL`.

## Collection via GitHub Actions (sketch)

`.github/workflows/collect.yml` (create when deploying):

```yaml
name: collect
on:
  schedule:
    - cron: "0 */6 * * *"   # every 6 hours
  workflow_dispatch:         # manual run button
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements.txt
      - run: python -m spacy download uk_core_news_sm
      - run: python -m scripts.run_pipeline
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

This keeps the **heavy NLP off the dashboard** — the Streamlit app only *reads*
the DB, so it stays light and fast.

## Controlling growth (optional)

Keep articles forever, but cap how many you ingest per run so growth is
predictable — e.g. a `max_articles` limit per source per collect. (See the
roadmap / Stage 11.) This is about tidy growth, not saving storage money.

## Protecting the DB under traffic

The expensive thing with many visitors is repeated DB reads. Cache them:

```python
@st.cache_data(ttl=300)   # 5 minutes
def load_analytics(): ...
```

So 100 visitors share one cached result instead of 100 queries.

## Secrets

Never commit `.env`. Put `DATABASE_URL` in:
- **Streamlit Cloud:** app → Settings → Secrets.
- **GitHub Actions:** repo → Settings → Secrets and variables → Actions.
