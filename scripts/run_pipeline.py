"""Run the full pipeline once for Ukrinform.

UA: Запускає весь конвеєр один раз для «Укрінформ».

Run / Запуск:
    python -m scripts.run_pipeline
"""

from app.collectors import UkrinformCollector, UnianCollector
from app.database.session import SessionLocal
from app.services import PipelineService


def main() -> None:
    """Collect, store and analyze the latest articles.

    UA: Збирає, зберігає та аналізує останні статті.
    """
    with SessionLocal() as db:
        for collector_cls in (UkrinformCollector, UnianCollector):
            report = PipelineService(db, collector_cls()).run()
            print(f"{collector_cls.source_name}: fetched={report.fetched} saved={report.saved} processed={report.processed}")


if __name__ == "__main__":
    main()
