"""Dictionary-based sentiment — count positive vs negative words.

UA: Тональність за словником: рахує позитивні та негативні слова.

Simple and transparent (no machine learning): we compare how many positive and
negative words appear. Input is lemmas from preprocessing, so the word lists are
also lemmas (base forms).
"""

from __future__ import annotations

from dataclasses import dataclass

#: Positive lemmas. / Позитивні леми.
POSITIVE_WORDS: frozenset[str] = frozenset(
    {
        "перемога", "успіх", "радість", "допомога", "підтримка", "свобода",
        "мир", "розвиток", "надія", "щастя", "добрий", "зростання",
        "досягнення", "відновлення", "вдячність", "любов", "співпраця",
    }
)

#: Negative lemmas. / Негативні леми.
NEGATIVE_WORDS: frozenset[str] = frozenset(
    {
        "війна", "смерть", "загибель", "руйнування", "атака", "удар", "жертва",
        "злочин", "криза", "втрата", "поранений", "вибух", "загроза",
        "корупція", "катастрофа", "обстріл", "біль", "страх", "трагедія",
        "знищення",
    }
)


@dataclass(frozen=True, slots=True)
class SentimentResult:
    """A sentiment label plus a score in [-1, 1].

    UA: Мітка тональності та оцінка в діапазоні [-1, 1].
    """

    label: str  # "positive" | "neutral" | "negative"
    score: float


def analyze_sentiment(lemmas: list[str]) -> SentimentResult:
    """Compare positive vs negative word counts.

    UA: Порівнює кількість позитивних і негативних слів.

    score = (positive - negative) / (positive + negative); 0.0 when the text has
    no sentiment words at all.
    """
    positive = sum(1 for word in lemmas if word in POSITIVE_WORDS)
    negative = sum(1 for word in lemmas if word in NEGATIVE_WORDS)
    total = positive + negative
    if total == 0:
        return SentimentResult("neutral", 0.0)

    score = round((positive - negative) / total, 3)
    if positive > negative:
        label = "positive"
    elif negative > positive:
        label = "negative"
    else:
        label = "neutral"
    return SentimentResult(label, score)
