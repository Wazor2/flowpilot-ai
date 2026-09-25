"""Check the configured PostgreSQL connection without printing its URL."""

from pathlib import Path
import sys

from sqlalchemy.exc import SQLAlchemyError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.database import engine


try:
    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")
except SQLAlchemyError as exc:
    original = getattr(exc, "orig", exc)
    print(f"PostgreSQL connection failed ({type(original).__name__}): {original}")
    raise SystemExit(1)

print("PostgreSQL connection OK.")
