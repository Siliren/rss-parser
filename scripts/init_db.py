"""Create the SQLite database and all tables.

UA: Створює базу даних SQLite і всі таблиці.

Run / Запуск:
    python -m scripts.init_db
"""

from app.database.session import engine, init_db


def main() -> None:
    """Create tables, then print where the database lives.

    UA: Створює таблиці й друкує шлях до бази даних.
    """
    init_db()
    print(f"Database ready at: {engine.url}")


if __name__ == "__main__":
    main()
