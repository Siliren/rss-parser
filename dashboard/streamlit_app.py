"""Streamlit dashboard — the project's UI.

UA: Дашборд Streamlit — інтерфейс проєкту.

Reads straight from the repositories (same database the pipeline writes to) and
shows: key metrics, an article table, a word cloud, sentiment and topic charts.
UI strings are translated via dashboard/i18n.py (language switcher in sidebar).

Run / Запуск:
    streamlit run dashboard/streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# `streamlit run dashboard/streamlit_app.py` puts the dashboard/ folder on the
# import path, not the project root — so add the root to make `import app` work.
# UA: Додаємо корінь проєкту до шляху, щоб працював import app.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import matplotlib.pyplot as plt  # noqa: E402  (must follow the sys.path fix)
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402
from matplotlib.font_manager import FontProperties, findfont  # noqa: E402
from sqlalchemy import select  # noqa: E402
from wordcloud import WordCloud  # noqa: E402

from app.database.models import Source  # noqa: E402
from app.database.repositories import AnalyticsRepository, ArticleRepository  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402
from dashboard.i18n import language_picker, t, t_sentiment, t_topic  # noqa: E402

st.set_page_config(page_title="Media NLP Analyzer", layout="wide")


def _cyrillic_font() -> str:
    """Path to a Cyrillic-capable font for the word cloud.

    UA: Шлях до шрифту з кирилицею для хмари слів.
    """
    return findfont(FontProperties(family="DejaVu Sans"))


def load_analytics() -> dict:
    """Read aggregated metrics. / Зчитує зведені метрики."""
    with SessionLocal() as db:
        repo = AnalyticsRepository(db)
        total, processed = repo.article_counts()
        return {
            "total": total,
            "processed": processed,
            "sentiment": repo.sentiment_counts(),
            "topics": repo.topic_counts(),
            "top_words": repo.top_words(100),
        }


def load_sources() -> list[tuple[int, str]]:
    """List sources as (id, name). / Список джерел як (id, назва)."""
    with SessionLocal() as db:
        rows = db.scalars(select(Source).order_by(Source.name)).all()
        return [(source.id, source.name) for source in rows]


def load_articles(source_id: int | None, limit: int) -> pd.DataFrame:
    """Read recent articles into a localized table. / Останні статті в таблицю."""
    with SessionLocal() as db:
        articles = ArticleRepository(db).get_articles(source_id=source_id, limit=limit)
        rows = []
        for article in articles:
            analysis = article.analysis_results[0] if article.analysis_results else None
            rows.append(
                {
                    t("source"): article.source.name,
                    t("col_topic"): t_topic(analysis.topic) if analysis else None,
                    t("col_sentiment"): (
                        t_sentiment(analysis.sentiment_label) if analysis else None
                    ),
                    t("col_score"): analysis.sentiment_score if analysis else None,
                    t("col_title"): article.title,
                    "URL": article.url,
                    t("col_date"): article.published_at,
                }
            )
    return pd.DataFrame(rows)


# --- Page ------------------------------------------------------------------

language_picker()  # sidebar switcher; sets st.session_state["lang"]

st.title(t("title"))
st.caption(t("caption"))

analytics = load_analytics()

col1, col2, col3 = st.columns(3)
col1.metric(t("metric_articles"), analytics["total"])
col2.metric(t("metric_processed"), analytics["processed"])
col3.metric(t("metric_topics"), len(analytics["topics"]))

if analytics["total"] == 0:
    st.info(t("empty_db"))
    st.stop()

tab_articles, tab_words, tab_sentiment, tab_topics, tab_url = st.tabs(
    [t("tab_articles"), t("tab_words"), t("tab_sentiment"), t("tab_topics"), t("tab_url")]
)

with tab_articles:
    sources = load_sources()
    options: dict[str, int | None] = {t("all_sources"): None}
    options.update({name: source_id for source_id, name in sources})
    choice = st.selectbox(t("source"), list(options))
    limit = st.slider(t("how_many"), 10, 200, 50, step=10)

    st.dataframe(
        load_articles(options[choice], limit),
        width="stretch",
        hide_index=True,
        column_config={"URL": st.column_config.LinkColumn("URL")},
    )

with tab_words:
    words = dict(analytics["top_words"])
    if words:
        cloud = WordCloud(
            width=900,
            height=400,
            background_color="white",
            font_path=_cyrillic_font(),
        ).generate_from_frequencies(words)
        figure, axes = plt.subplots(figsize=(9, 4))
        axes.imshow(cloud, interpolation="bilinear")
        axes.axis("off")
        st.pyplot(figure)

        top20 = pd.DataFrame(
            analytics["top_words"][:20], columns=[t("word"), t("count")]
        ).set_index(t("word"))
        st.bar_chart(top20)
    else:
        st.info(t("no_words"))

with tab_sentiment:
    sentiment = analytics["sentiment"]
    if sentiment:
        localized = {t_sentiment(label): n for label, n in sentiment.items()}
        st.bar_chart(pd.DataFrame({t("count"): localized}))
    else:
        st.info(t("no_sentiment"))

with tab_topics:
    topics = analytics["topics"]
    if topics:
        data = [(t_topic(name), n) for name, n in topics]
        frame = pd.DataFrame(data, columns=[t("topic"), t("count")]).set_index(t("topic"))
        st.bar_chart(frame)
    else:
        st.info(t("no_topics"))

with tab_url:
    st.write(t("paste_url"))
    url_input = st.text_input("URL", key="analyze_url", label_visibility="collapsed")
    if st.button(t("analyze")) and url_input:
        # Imported lazily so the spaCy model loads only when this is used.
        # UA: Імпорт лінивий — модель завантажується лише за потреби.
        from app.services import analyze_url

        with st.spinner(t("analyzing")):
            try:
                result = analyze_url(url_input)
            except Exception as exc:  # show a friendly message in the UI
                st.error(f"{t('analyze_failed')}: {exc}")
            else:
                if result.title:
                    st.subheader(result.title)
                m1, m2, m3 = st.columns(3)
                m1.metric(t("col_topic"), t_topic(result.topic))
                m2.metric(
                    t("col_sentiment"),
                    t_sentiment(result.sentiment_label),
                    f"{result.sentiment_score:+.2f}",
                )
                m3.metric(t("url_words"), result.word_count)
                if result.top_words:
                    words_df = pd.DataFrame(
                        result.top_words, columns=[t("word"), t("count")]
                    ).set_index(t("word"))
                    st.bar_chart(words_df)
