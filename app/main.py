"""FastAPI application entrypoint.

UA: Точка входу застосунку FastAPI.
"""

from fastapi import FastAPI

from app.api.routers import analytics, analyze, articles, collect

app = FastAPI(
    title="Media NLP Analyzer",
    version="0.1.0",
    description="Ukrainian media NLP analysis pipeline API",
)

app.include_router(articles.router)
app.include_router(analytics.router)
app.include_router(collect.router)
app.include_router(analyze.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Simple liveness probe for local dev and deploy checks."""
    return {"status": "ok"}
