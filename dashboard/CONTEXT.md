# Context — `dashboard/`

> **UA:** Дашборд Streamlit: показує статті, хмару слів та графіки.
>
> The Streamlit UI. Reads from the repositories (the same DB the pipeline fills)
> and visualizes the results. No analysis happens here — display only.
> **Status:** Stage 10 ✅ done.

## Purpose

Give a human-friendly view of what the pipeline produced: how many articles,
which topics, overall sentiment, and the most common words.

## Files

- `streamlit_app.py` — the whole dashboard (one file, on purpose).
- `i18n.py` — dictionary-based translations + the sidebar language switcher.

## Language switcher (i18n)

Two languages: **Українська / English**, picked in the sidebar.

- No dependency — just dicts in `i18n.py`. The chosen code lives in
  `st.session_state["lang"]`; Streamlit reruns the script so everything
  re-renders in the new language.
- `t("key")` translates UI strings; `t_sentiment(label)` / `t_topic(name)`
  translate stored data values (e.g. `negative`→«негативна», `війна`→`war`).
- **Add a new label:** add the key to **both** languages in `_STRINGS`, then use
  `t("your_key")` in `streamlit_app.py`.

## What it shows

- **Metrics:** total articles, processed, number of topics.
- **Tab «Статті»:** filterable article table (source, topic, sentiment, title,
  clickable URL, date).
- **Tab «Частота слів»:** word cloud + top-20 bar chart.
- **Tab «Тональність»:** sentiment bar chart.
- **Tab «Теми»:** topic bar chart.

If the DB is empty it shows a hint to run `python -m scripts.run_pipeline` and
stops.

## Run

```bash
streamlit run dashboard/streamlit_app.py     # http://localhost:8501
```

## Design decisions

- Reads the DB **directly via repositories** (`AnalyticsRepository`,
  `ArticleRepository`) — simplest for a same-machine app; it does not call the
  FastAPI layer.
- Word cloud uses matplotlib's **DejaVu Sans** font (`font_path`) so Cyrillic
  renders instead of empty boxes.
- Charts use Streamlit's built-in `st.bar_chart` (pandas DataFrames) to stay
  simple; matplotlib is only used for the word-cloud image.
- **Path bootstrap:** `streamlit run dashboard/streamlit_app.py` puts the
  `dashboard/` folder (not the project root) on `sys.path`, so the file inserts
  the project root at the top before `import app...`. Without it you get
  `ModuleNotFoundError: No module named 'app'`.

## Tested by

Verified with Streamlit's `AppTest` harness (runs the script server-side):
no exceptions, metrics/tabs/table render against the real DB (132 articles).

## Next that touches this layer

Stage 11 — periodic collection keeps the data fresh; Stage 12 — deploy
(Streamlit Cloud).
