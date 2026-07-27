"""Preprocessing — clean raw text and reduce it to meaningful lemmas.

UA: Препроцесинг: очищує текст і зводить його до значущих лем.

Pipeline: clean HTML/whitespace -> lemmatize (spaCy) -> drop stopwords.
"""

from app.preprocessing.cleaner import clean_text
from app.preprocessing.lemmatizer import get_nlp, lemmatize
from app.preprocessing.stopwords import STOPWORDS, remove_stopwords
from app.preprocessing.tokenizer import tokenize


def preprocess(raw: str) -> list[str]:
    """Turn raw text into a list of clean lemmas (stopwords removed).

    UA: Перетворює сирий текст на список чистих лем (без стоп-слів).
    """
    return lemmatize(clean_text(raw), drop_stopwords=True)


__all__ = [
    "preprocess",
    "clean_text",
    "tokenize",
    "remove_stopwords",
    "STOPWORDS",
    "lemmatize",
    "get_nlp",
]
