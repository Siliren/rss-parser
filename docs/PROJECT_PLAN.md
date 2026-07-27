# Project Plan — media-nlp-analyzer

> **For AI:** Read this file first. Continue from `Current Focus` / `Next Task`.
> Update status after each completed stage.

## Goal

Ukrainian media NLP analyzer: scrape news → preprocess → analyze → visualize in Streamlit.

## Stack (fixed — do not change without user request)

- Python 3.10+ (developed on 3.10), SQLite (dev), SQLAlchemy 2.0, FastAPI, Streamlit
- httpx + BeautifulSoup4 + lxml, trafilatura, spaCy (`uk_core_news_sm`)
- **NO** Django, **NO** Celery, **NO** GPT/LLM API

## Data Pipeline

```
News website / Telegram
        ↓
  Collect raw data
        ↓
  Save raw articles (SQLite)
        ↓
  Clean HTML/text → tokenize → stopwords → lemmatize
        ↓
  NLP: frequency + sentiment + topics
        ↓
  Save analysis results
        ↓
  Streamlit dashboard + FastAPI
```

## MVP v1.0 Checklist

- [x] 2 news site collectors (Ukrinform + UNIAN)
- [x] SQLite tables: sources, articles, analysis_results, word_frequencies
- [x] Preprocessing: clean, tokenize, stopwords, lemmatize
- [x] Analysis: frequency, sentiment (dictionary), topic (keywords)
- [x] PipelineService orchestrator
- [x] Streamlit: articles list, word cloud, sentiment chart

## Roadmap

| Stage | Task | Status | Notes |
|-------|------|--------|-------|
| 1 | Repo, venv, folder structure, README | ✅ DONE | venv on Python 3.10; core deps in requirements-core.txt |
| 2 | SQLAlchemy models + session + init_db | ✅ DONE | sources, articles, analysis_results, word_frequencies |
| 3 | First collector (1 news site) | ✅ DONE | Ukrinform RSS; BaseCollector + RawArticle. Pravda blocked by Cloudflare |
| 4 | Article repository + dedup by URL | ✅ DONE | ArticleRepository: get_or_create_source, save_articles, get_articles |
| 5 | Preprocessing modules | ✅ DONE | cleaner, tokenizer, stopwords, lemmatizer; spacy + uk_core_news_sm installed |
| 6 | Analysis modules | ✅ DONE | frequency, sentiment (dictionary), topic_detection (keywords) |
| 7 | PipelineService | ✅ DONE | collect → save → process → analyze → store; idempotent; scripts/run_pipeline.py |
| 8 | Second collector | ✅ DONE | UNIAN; refactored shared RssCollector base (Ukrinform+UNIAN are config-only) |
| 9 | FastAPI endpoints | ✅ DONE | GET /articles, GET /analytics, POST /collect/{source}; thin routers + schemas |
| 10 | Streamlit dashboard (full) | ✅ DONE | metrics + tabs: Статті, Частота слів, Тональність, Теми; word cloud (Cyrillic font) |
| 11 | APScheduler (periodic collect) | ⏸ DEFERRED | Not needed until the project is live. When deploying, prefer a GitHub Actions cron (see docs/DEPLOY.md) + an ingest cap; not a local scheduler. |
| 12 | Deploy | 🔜 WHEN LIVE | Streamlit Cloud + free Postgres + Actions cron — recipe in docs/DEPLOY.md |

## Current Focus

**MVP v1.0 — COMPLETE 🎉** plus extras (analyze-a-URL, dashboard i18n).
48 tests pass. Project runs end to end locally; **not deployed**.

## Next Task

Nothing required — the MVP is done. Optional, only when you decide to go live:

- **Deploy (Stage 12):** follow `docs/DEPLOY.md` (Streamlit Cloud + free Postgres
  + GitHub Actions cron). Switching SQLite→Postgres is one `DATABASE_URL` line.
- **Then revisit Stage 11** ideas in the live context: cap ingest per source
  (`max_articles`) and add `st.cache_data` to dashboard reads to protect the DB
  under traffic. Articles are kept forever (storage is tiny — see docs/DEPLOY.md).

## Architecture Rules

1. Collectors do not know about analysis or SQL
2. Analysis modules are pure functions (text in → metrics out)
3. Services orchestrate; routers are thin HTTP layer
4. Raw content and cleaned content stored separately
5. Dedup by `url` (unique constraint)

## Database Schema (planned — Stage 2)

```
sources (1) ──< articles (1) ──< analysis_results
                          └──< word_frequencies
```

## Extra Features (beyond original roadmap)

| Feature | Status | Notes |
|---------|--------|-------|
| Analyze any URL (stateless) | ✅ DONE | `POST /analyze` + dashboard tab; trafilatura extraction; SSRF guard (`app/utils/url_safety.py`); not saved to DB |
| Dashboard i18n (UK/EN) | ✅ DONE | `dashboard/i18n.py` dict-based + sidebar switcher; translates UI, sentiment labels, topic names; no new dependency |

## Session Log

| Date | Stage | What was done |
|------|-------|---------------|
| 2026-06-24 | 1 | venv 3.14.6, structure, README, core+streamlit deps, pytest pass; spacy → Stage 5 |
| 2026-06-28 | 2 | Models (Source/Article/AnalysisResult/WordFrequency), session.py, init_db, tests (4 pass); added docs/ARCHITECTURE.md + per-module CONTEXT.md convention; bilingual EN/UA docstrings |
| 2026-06-28 | 3 | BaseCollector + RawArticle + UkrinformCollector (RSS via lxml); 3 collector tests (7 total pass); live fetch = 30 articles. Pravda blocked by Cloudflare → switched to Ukrinform; collectors/CONTEXT.md added |
| 2026-06-28 | 4 | ArticleRepository (get_or_create_source, save_articles+dedup, get_articles); 4 tests (11 total pass); live e2e: 30 saved, re-run 0 (dedup); repositories/CONTEXT.md added |
| 2026-06-28 | 5 | Preprocessing: cleaner, tokenizer, stopwords, lemmatizer (spaCy uk_core_news_sm) + preprocess(); 5 tests (16 total, model tests skip if absent); spaCy+pymorphy3 installed; docs/DEPENDENCIES.md + preprocessing/CONTEXT.md added |
| 2026-06-28 | 6 | Analysis: frequency (Counter), sentiment (dictionary), topic_detection (keywords); 7 tests (23 total pass); verified live on stored articles; analysis/CONTEXT.md added |
| 2026-06-28 | 7 | PipelineService + PipelineReport; repo.get_unprocessed_articles + save_analysis; collector.base_url; scripts/run_pipeline.py; 3 tests (26 total pass); live: 32 processed, 481 word_freqs, idempotent; services/CONTEXT.md added |
| 2026-06-28 | 8 | Second collector UNIAN; refactored shared RssCollector base (Ukrinform+UNIAN config-only); 2 tests (28 total pass); live: UNIAN 100 processed. DB retention noted for Stage 11 |
| 2026-06-28 | 9 | FastAPI: GET /articles, GET /analytics, POST /collect/{source}; AnalyticsRepository; schemas (ArticleOut/AnalyticsOut/LabelCount/CollectResponse); routers wired in main.py; 5 tests (33 total pass); live vs real DB (132 articles); api/CONTEXT.md added |
| 2026-06-28 | 10 | Streamlit dashboard: metrics + 4 tabs (articles table, word cloud w/ Cyrillic font, sentiment + topic charts); reads repositories directly; verified via AppTest (no exceptions); dashboard/CONTEXT.md added. MVP v1.0 complete |
| 2026-06-28 | + | Analyze-any-URL feature (stateless): url_safety SSRF guard, url_analysis_service (trafilatura), POST /analyze, 5th dashboard tab; 7 tests (48 total pass); live: full article extracted (109 words), SSRF blocked; docs/DEPLOY.md added |
