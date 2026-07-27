"""Word frequency — count how often each lemma appears.

UA: Частота слів: рахує, скільки разів трапляється кожна лема.
"""

from __future__ import annotations

from collections import Counter


def word_frequencies(
    lemmas: list[str], top_n: int | None = None
) -> list[tuple[str, int]]:
    """Count lemmas and return (word, count) pairs, most frequent first.

    UA: Рахує леми й повертає пари (слово, кількість), спершу найчастіші.

    `top_n=None` returns every word.
    """
    return Counter(lemmas).most_common(top_n)
