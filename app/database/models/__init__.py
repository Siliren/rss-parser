"""Model registry. Importing this package registers every table on Base.metadata."""

from app.database.models.analysis import AnalysisResult, WordFrequency
from app.database.models.article import Article
from app.database.models.source import Source

__all__ = ["Source", "Article", "AnalysisResult", "WordFrequency"]
