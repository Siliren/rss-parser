"""Topic detection — match article words against keyword sets.

UA: Визначення теми: зіставляє слова статті з наборами ключових слів.

The topic with the most keyword matches wins. Keywords are lemmas (base forms),
to match preprocessing output.
"""

from __future__ import annotations

#: Returned when nothing matches. / Повертається, коли немає збігів.
OTHER = "інше"

TOPIC_KEYWORDS: dict[str, frozenset[str]] = {
    "війна": frozenset(
        {
            "війна", "фронт", "обстріл", "армія", "зброя", "бій", "окупант",
            "ракета", "дрон", "наступ", "військовий", "оборона",
        }
    ),
    "політика": frozenset(
        {
            "політика", "президент", "парламент", "депутат", "закон", "уряд",
            "вибори", "міністр", "влада", "партія",
        }
    ),
    "економіка": frozenset(
        {
            "економіка", "бюджет", "інфляція", "ціна", "ринок", "податок",
            "бізнес", "гривня", "інвестиція", "торгівля",
        }
    ),
    "суспільство": frozenset(
        {
            "суспільство", "освіта", "культура", "школа", "медицина", "родина",
            "студент", "мова",
        }
    ),
    "спорт": frozenset(
        {
            "спорт", "матч", "команда", "гравець", "чемпіонат", "олімпіада",
            "гол", "турнір", "змагання",
        }
    ),
}


def detect_topic(lemmas: list[str]) -> str:
    """Return the topic with the most keyword hits, or "інше" if none.

    UA: Повертає тему з найбільшою кількістю збігів; інакше «інше».
    """
    words = set(lemmas)
    best_topic = OTHER
    best_hits = 0
    for topic, keywords in TOPIC_KEYWORDS.items():
        hits = len(words & keywords)
        if hits > best_hits:
            best_hits = hits
            best_topic = topic
    return best_topic
