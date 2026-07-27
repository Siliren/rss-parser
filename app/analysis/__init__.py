"""Analysis — pure functions: lemmas in, metrics out.

UA: Аналіз: чисті функції — леми на вході, метрики на виході.
"""

from app.analysis.frequency import word_frequencies
from app.analysis.sentiment import (
    NEGATIVE_WORDS,
    POSITIVE_WORDS,
    SentimentResult,
    analyze_sentiment,
)
from app.analysis.topic_detection import TOPIC_KEYWORDS, detect_topic

__all__ = [
    "word_frequencies",
    "analyze_sentiment",
    "SentimentResult",
    "POSITIVE_WORDS",
    "NEGATIVE_WORDS",
    "detect_topic",
    "TOPIC_KEYWORDS",
]
