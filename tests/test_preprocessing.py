"""Tests for the preprocessing modules (Stage 5).

UA: Тести модулів препроцесингу.

Cleaner/tokenizer/stopwords run without the spaCy model. Lemmatizer tests skip
automatically if `uk_core_news_sm` is not installed.
"""

import pytest
import spacy.util

from app.preprocessing import (
    clean_text,
    lemmatize,
    preprocess,
    remove_stopwords,
    tokenize,
)
from app.preprocessing.lemmatizer import MODEL_NAME

needs_model = pytest.mark.skipif(
    not spacy.util.is_package(MODEL_NAME),
    reason=f"{MODEL_NAME} not installed",
)


def test_clean_text_strips_html_and_whitespace():
    """HTML tags go, whitespace collapses. / Прибирає HTML і зайві пробіли."""
    assert clean_text("<p>Привіт   <b>світ</b>!</p>\n") == "Привіт світ !"


def test_tokenize_lowercases_and_drops_non_words():
    """Words only, lowercase; digits/punctuation dropped. / Лише слова."""
    assert tokenize("Привіт, СВІТ! 123 об'єкт") == ["привіт", "світ", "об'єкт"]


def test_remove_stopwords_filters_common_words():
    """Stopwords removed, content words kept. / Стоп-слова прибрано."""
    result = remove_stopwords(["і", "новина", "та", "Київ"])
    assert "новина" in result
    assert "київ" in [w.lower() for w in result]
    assert "і" not in result and "та" not in result


@needs_model
def test_lemmatize_returns_lowercase_base_forms():
    """Inflected words reduce to base forms; stopwords dropped. / Леми, без стоп-слів."""
    lemmas = lemmatize("Це нові новини про Київ")
    assert lemmas == [w.lower() for w in lemmas]  # all lowercase
    assert "це" not in lemmas  # stopword removed
    assert "новина" in lemmas  # новини -> новина


@needs_model
def test_preprocess_full_pipeline():
    """clean -> lemmatize -> drop stopwords. / Повний конвеєр препроцесингу."""
    lemmas = preprocess("<p>Це <b>нові</b> новини!</p>")
    assert "новина" in lemmas
    assert "це" not in lemmas
