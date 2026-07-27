"""Tests for the analysis modules (Stage 6).

UA: Тести модулів аналізу.

Pure functions over lemma lists — no spaCy model or DB needed.
"""

from app.analysis import analyze_sentiment, detect_topic, word_frequencies


def test_word_frequencies_counts_and_orders():
    """Most frequent first; top_n limits. / Спершу найчастіші; top_n обмежує."""
    lemmas = ["новина", "київ", "новина", "новина", "київ"]
    assert word_frequencies(lemmas, top_n=2) == [("новина", 3), ("київ", 2)]


def test_word_frequencies_empty():
    """Empty input → empty list. / Порожній вхід → порожній список."""
    assert word_frequencies([]) == []


def test_sentiment_positive():
    """Positive words → positive label, score > 0. / Позитив."""
    result = analyze_sentiment(["перемога", "успіх", "радість"])
    assert result.label == "positive"
    assert result.score > 0


def test_sentiment_negative():
    """Negative words → negative label, score < 0. / Негатив."""
    result = analyze_sentiment(["війна", "смерть", "обстріл"])
    assert result.label == "negative"
    assert result.score < 0


def test_sentiment_neutral_without_sentiment_words():
    """No sentiment words → neutral, score 0.0. / Нейтрально."""
    result = analyze_sentiment(["новина", "київ", "погода"])
    assert result.label == "neutral"
    assert result.score == 0.0


def test_detect_topic_picks_best_match():
    """Most keyword hits wins. / Перемагає тема з найбільшою кількістю збігів."""
    assert detect_topic(["обстріл", "армія", "місто"]) == "війна"


def test_detect_topic_other_when_no_keywords():
    """No keywords → "інше". / Немає ключових слів → «інше»."""
    assert detect_topic(["котик", "сонце"]) == "інше"
