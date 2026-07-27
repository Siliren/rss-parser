"""Lemmatizer — base word forms via the spaCy Ukrainian model.

UA: Лематизатор: базові форми слів через українську модель spaCy.

The model (uk_core_news_sm) is heavy, so it is loaded once and cached.
"""

from __future__ import annotations

import functools

import spacy

MODEL_NAME = "uk_core_news_sm"


@functools.lru_cache(maxsize=1)
def get_nlp() -> spacy.language.Language:
    """Load the Ukrainian model once and reuse it (cached).

    UA: Завантажує українську модель один раз і кешує її.
    """
    return spacy.load(MODEL_NAME)


def lemmatize(text: str, *, drop_stopwords: bool = True) -> list[str]:
    """Return lowercase lemmas of the word tokens in `text`.

    UA: Повертає леми слів із тексту в нижньому регістрі.

    Keeps only alphabetic tokens; drops stopwords by default.
    """
    doc = get_nlp()(text)
    return [
        token.lemma_.lower()
        for token in doc
        if token.is_alpha and not (drop_stopwords and token.is_stop)
    ]
