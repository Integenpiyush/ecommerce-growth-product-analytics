"""
Database Connection & Engine Management
=======================================
Provides database connectivity supporting both PostgreSQL (production)
and SQLite (local demo & standalone Streamlit mode).
"""

import os
import logging
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

logger = logging.getLogger(__name__)


def get_db_url() -> str:
    """
    Determine the database URL based on environment variables.
    If POSTGRES_URL is provided, it connects to PostgreSQL.
    Otherwise, it defaults to a local SQLite database file in data/processed/ecommerce.db.
    """
    pg_url = os.getenv("POSTGRES_URL")
    if pg_url:
        return pg_url

    pg_user = os.getenv("POSTGRES_USER")
    pg_password = os.getenv("POSTGRES_PASSWORD")
    pg_host = os.getenv("POSTGRES_HOST")
    pg_port = os.getenv("POSTGRES_PORT", "5432")
    pg_db = os.getenv("POSTGRES_DB")

    if pg_user and pg_password and pg_host and pg_db and os.getenv("DB_DIALECT") == "postgresql":
        return f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"

    # Default fallback to SQLite demo database
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sqlite_path = os.getenv("DB_PATH", os.path.join(base_dir, "data", "processed", "ecommerce.db"))
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    return f"sqlite:///{sqlite_path}"


def get_engine(db_url: Optional[str] = None) -> Engine:
    """Create and return a SQLAlchemy engine with connection pooling."""
    url = db_url or get_db_url()
    is_sqlite = url.startswith("sqlite")

    if is_sqlite:
        engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            echo=False
        )
    else:
        engine = create_engine(
            url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=False
        )
    return engine


def init_db(engine: Optional[Engine] = None, ddl_path: Optional[str] = None) -> None:
    """
    Initialize database schema by executing DDL statements.
    Automatically detects PostgreSQL vs SQLite.
    """
    engine = engine or get_engine()
    is_sqlite = "sqlite" in str(engine.url)

    if ddl_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if is_sqlite:
            ddl_path = os.path.join(base_dir, "sql", "ddl", "schema_sqlite.sql")
        else:
            ddl_path = os.path.join(base_dir, "sql", "ddl", "schema_postgresql.sql")

    logger.info(f"Initializing database schema from {ddl_path}...")
    with open(ddl_path, "r", encoding="utf-8") as f:
        ddl_script = f.read()

    # Split statements for execution
    statements = [stmt.strip() for stmt in ddl_script.split(";") if stmt.strip()]

    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))

    logger.info("Database schema initialized successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    eng = get_engine()
    print(f"Connected to database engine: {eng.url}")
    init_db(eng)
