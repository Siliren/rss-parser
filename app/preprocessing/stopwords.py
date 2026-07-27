"""Ukrainian stopwords and a filter.

UA: Українські стоп-слова та фільтр.

The list comes from spaCy's Ukrainian language data (no model download needed).
"""

from __future__ import annotations

from spacy.lang.uk.stop_words import STOP_WORDS

#: Ukrainian stopwords, lowercased. / Українські стоп-слова в нижньому регістрі.
STOPWORDS: frozenset[str] = frozenset(word.lower() for word in STOP_WORDS)


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Drop tokens that are Ukrainian stopwords (case-insensitive).

    UA: Прибирає токени, що є українськими стоп-словами.
    """
    return [token for token in tokens if token.lower() not in STOPWORDS]
