"""Tiny i18n for the dashboard — dictionary-based, no extra dependency.

UA: Проста локалізація дашборду — на словниках, без зайвих залежностей.

How it works: the chosen language code lives in `st.session_state["lang"]`.
`t("key")` looks the key up for that language. Streamlit reruns the whole script
on every interaction, so switching language just re-renders everything.

    from dashboard.i18n import t, language_picker
    language_picker()          # draws the sidebar switcher + stores the choice
    st.title(t("title"))
"""

from __future__ import annotations

import streamlit as st

# language code -> name shown in the switcher / код мови -> назва у перемикачі
LANGUAGES = {"uk": "Українська", "en": "English"}
DEFAULT_LANG = "uk"

# UI strings. Add a key here in BOTH languages to make a new label translatable.
_STRINGS: dict[str, dict[str, str]] = {
    "uk": {
        "title": "📰 Аналізатор українського медіапростору",
        "caption": "Аналіз українського медіапростору засобами NLP",
        "language": "🌐 Мова",
        "metric_articles": "Статей",
        "metric_processed": "Оброблено",
        "metric_topics": "Тем",
        "empty_db": "База порожня. Запустіть конвеєр: `python -m scripts.run_pipeline`.",
        "tab_articles": "Статті",
        "tab_words": "Частота слів",
        "tab_sentiment": "Тональність",
        "tab_topics": "Теми",
        "tab_url": "Аналіз за URL",
        "source": "Джерело",
        "all_sources": "Усі джерела",
        "how_many": "Скільки показати",
        "col_topic": "Тема",
        "col_sentiment": "Тональність",
        "col_score": "Оцінка",
        "col_title": "Заголовок",
        "col_date": "Дата",
        "word": "Слово",
        "count": "Кількість",
        "topic": "Тема",
        "no_words": "Немає даних про слова.",
        "no_sentiment": "Немає даних про тональність.",
        "no_topics": "Немає даних про теми.",
        "paste_url": "Вставте посилання на статтю",
        "analyze": "Аналізувати",
        "analyzing": "Завантаження та аналіз…",
        "analyze_failed": "Не вдалося проаналізувати",
        "url_words": "Слів",
    },
    "en": {
        "title": "📰 Ukrainian Media NLP Analyzer",
        "caption": "Analyzing Ukrainian media with NLP",
        "language": "🌐 Language",
        "metric_articles": "Articles",
        "metric_processed": "Processed",
        "metric_topics": "Topics",
        "empty_db": "The database is empty — run: `python -m scripts.run_pipeline`.",
        "tab_articles": "Articles",
        "tab_words": "Word frequency",
        "tab_sentiment": "Sentiment",
        "tab_topics": "Topics",
        "tab_url": "Analyze a URL",
        "source": "Source",
        "all_sources": "All sources",
        "how_many": "How many",
        "col_topic": "Topic",
        "col_sentiment": "Sentiment",
        "col_score": "Score",
        "col_title": "Title",
        "col_date": "Date",
        "word": "Word",
        "count": "Count",
        "topic": "Topic",
        "no_words": "No word data yet.",
        "no_sentiment": "No sentiment data yet.",
        "no_topics": "No topic data yet.",
        "paste_url": "Paste an article URL",
        "analyze": "Analyze",
        "analyzing": "Fetching and analyzing…",
        "analyze_failed": "Could not analyze",
        "url_words": "Words",
    },
}

# Data values (stored in English/Ukrainian) -> display text per language.
_SENTIMENT = {
    "uk": {"positive": "позитивна", "neutral": "нейтральна", "negative": "негативна"},
    "en": {"positive": "positive", "neutral": "neutral", "negative": "negative"},
}
_TOPICS = {
    "uk": {
        "війна": "війна", "політика": "політика", "економіка": "економіка",
        "суспільство": "суспільство", "спорт": "спорт", "інше": "інше",
    },
    "en": {
        "війна": "war", "політика": "politics", "економіка": "economy",
        "суспільство": "society", "спорт": "sport", "інше": "other",
    },
}


def current_lang() -> str:
    """The selected language code (defaults to uk). / Поточна мова."""
    return st.session_state.get("lang", DEFAULT_LANG)


def t(key: str) -> str:
    """Translate a UI string key for the current language.

    UA: Перекладає ключ рядка інтерфейсу для поточної мови.
    """
    return _STRINGS.get(current_lang(), _STRINGS[DEFAULT_LANG]).get(key, key)


def t_sentiment(label: str) -> str:
    """Localized sentiment label. / Локалізована мітка тональності."""
    return _SENTIMENT.get(current_lang(), {}).get(label, label)


def t_topic(topic: str) -> str:
    """Localized topic name. / Локалізована назва теми."""
    return _TOPICS.get(current_lang(), {}).get(topic, topic)


def language_picker() -> str:
    """Draw the sidebar language switcher and store the choice. Returns the code.

    UA: Малює перемикач мови в бічній панелі та зберігає вибір.
    """
    codes = list(LANGUAGES)
    current = current_lang()
    selected = st.sidebar.radio(
        t("language"),
        options=codes,
        format_func=lambda code: LANGUAGES[code],
        index=codes.index(current) if current in codes else 0,
    )
    st.session_state["lang"] = selected
    return selected
