import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is required. Configure PostgreSQL explicitly; "
        "only tests may set DATABASE_URL to sqlite:///:memory:."
    )
if DATABASE_URL.startswith("sqlite") and DATABASE_URL not in {"sqlite:///:memory:", "sqlite+pysqlite:///:memory:"}:
    raise RuntimeError("File-backed SQLite is disabled; use PostgreSQL or sqlite:///:memory: for tests.")

engine_kwargs = {"connect_args": {"check_same_thread": False}} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
