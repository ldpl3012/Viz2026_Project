"""SQLAlchemy connection configuration for MySQL and PostgreSQL."""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv(Path(__file__).resolve().parent / ".env")

Base = declarative_base()


def _database_url():
    engine_name = os.getenv("DB_ENGINE", "mysql").strip().lower()
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "root")
    host = os.getenv("DB_HOST", "localhost")
    database = os.getenv("DB_NAME", "Viz2026")

    if engine_name == "mysql":
        drivername = "mysql+pymysql"
        default_port = 3306
    elif engine_name in ("postgres", "postgresql"):
        drivername = "postgresql+psycopg2"
        default_port = 5432
    else:
        raise ValueError(
            "DB_ENGINE must be 'mysql' or 'postgresql', "
            f"not {engine_name!r}."
        )

    port = int(os.getenv("DB_PORT", str(default_port)))
    return URL.create(
        drivername=drivername,
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
    )


def get_engine():
    """Return a SQLAlchemy engine for the configured database."""
    return create_engine(_database_url(), pool_pre_ping=True)


def get_session():
    """Create and return a SQLAlchemy ORM session."""
    return sessionmaker(bind=get_engine())()
