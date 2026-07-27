"""Pydantic DTOs — the shapes the API sends back."""

from app.schemas.analytics import AnalyticsOut, LabelCount
from app.schemas.article import ArticleOut
from app.schemas.collect import CollectResponse
from app.schemas.url_analysis import UrlAnalysisOut, UrlAnalysisRequest

__all__ = [
    "ArticleOut",
    "AnalyticsOut",
    "LabelCount",
    "CollectResponse",
    "UrlAnalysisRequest",
    "UrlAnalysisOut",
]
