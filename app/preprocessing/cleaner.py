"""Text cleaner — strip HTML and tidy whitespace.

UA: Очищувач тексту: прибирає HTML і зайві пробіли.
"""

from __future__ import annotations

from bs4 import BeautifulSoup


def clean_text(raw: str) -> str:
    """Remove HTML tags and collapse whitespace into single spaces.

    UA: Видаляє HTML-теги та згортає пробіли в один.
    """
    text = BeautifulSoup(raw or "", "html.parser").get_text(separator=" ")
    return " ".join(text.split())
