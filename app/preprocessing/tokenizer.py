"""Tokenizer — split text into lowercase word tokens (no spaCy needed).

UA: Токенізатор: розбиває текст на слова в нижньому регістрі (без spaCy).

This is the lightweight path: fast, dependency-free word splitting when you
don't need linguistic base forms. For base forms use `lemmatizer.lemmatize`.
"""

from __future__ import annotations

import re

# Letters (any language, no digits/underscore), allowing an apostrophe inside
# a word (e.g. об'єкт, п'ять). / Літери + апостроф усередині слова.
_WORD = re.compile(r"[^\W\d_]+(?:['ʼ’][^\W\d_]+)*", re.UNICODE)


def tokenize(text: str) -> list[str]:
    """Return lowercase word tokens; drops digits and punctuation.

    UA: Повертає слова в нижньому регістрі; цифри й пунктуацію відкидає.
    """
    return [match.group().lower() for match in _WORD.finditer(text)]
