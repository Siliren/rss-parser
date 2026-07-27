"""Repositories — data-access helpers that wrap the database."""

from app.database.repositories.analytics_repository import AnalyticsRepository
from app.database.repositories.article_repository import ArticleRepository

__all__ = ["ArticleRepository", "AnalyticsRepository"]
