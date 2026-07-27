"""/collect endpoint — run the pipeline for a source on demand.

UA: Ендпоінт /collect — запуск конвеєра для джерела за запитом.

Note: this runs synchronously (fetch + NLP), so the request can take a few
seconds. Fine for a small educational project.
"""

from __future__ import annotations

from enum import Enum

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.collectors import UkrinformCollector, UnianCollector
from app.database.session import get_db
from app.schemas import CollectResponse
from app.services import PipelineService

router = APIRouter(prefix="/collect", tags=["collect"])


class SourceName(str, Enum):
    """Sources the API can collect. / Джерела, які вміє збирати API."""

    ukrinform = "ukrinform"
    unian = "unian"


# Maps the URL name to its collector class. / Звʼязок назви з класом збирача.
COLLECTORS = {
    SourceName.ukrinform: UkrinformCollector,
    SourceName.unian: UnianCollector,
}


@router.post("/{source}", response_model=CollectResponse)
def collect_source(
    source: SourceName,
    db: Session = Depends(get_db),
) -> CollectResponse:
    """Collect, store and analyze the latest articles for one source.

    UA: Збирає, зберігає та аналізує останні статті одного джерела.
    """
    collector = COLLECTORS[source]()
    report = PipelineService(db, collector).run()
    return CollectResponse(
        source=collector.source_name,
        fetched=report.fetched,
        saved=report.saved,
        processed=report.processed,
    )
