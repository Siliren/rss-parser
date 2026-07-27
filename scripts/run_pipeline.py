"""Run the full pipeline once for Ukrinform.

UA: Запускає весь конвеєр один раз для «Укрінформ».

Run / Запуск:
    python -m scripts.run_pipeline
"""

from app.collectors import UkrinformCollector
from app.database.session import SessionLocal
from app.services import PipelineService


def main() -> None:
    """Collect, store and analyze the latest articles.

    UA: Збирає, зберігає та аналізує останні статті.
    """
    with SessionLocal() as db:
        report = PipelineService(db, UkrinformCollector()).run()

    print(
        f"fetched={report.fetched} "
        f"saved={report.saved} "
        f"processed={report.processed}"
    )


if __name__ == "__main__":
    main()
