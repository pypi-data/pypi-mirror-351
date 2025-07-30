"""Test fixtures for psycopg-toolbox."""

import os
from dataclasses import dataclass
from collections.abc import AsyncGenerator

import pytest

from .logging import LoggingConnection
from .query_helpers import create_database, drop_database


@dataclass
class DBConfig:
    """Database configuration for tests."""

    dbname: str
    user: str
    host: str
    port: int
    password: str | None


@pytest.fixture(scope="session")
def psycopg_toolbox_db_name() -> str:
    """Generate a unique database name for testing.

    This fixture:
    1. Uses the worker ID from pytest-xdist if running in parallel
    2. Can be overridden by passing a custom name to psycopg_toolbox_db

    Returns:
        A unique database name suitable for testing
    """
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "gw0")
    return f"psycopg_toolbox_{worker_id}"


@pytest.fixture(scope="session")
def db_config(psycopg_toolbox_db_name: str) -> DBConfig:
    """Provide database configuration for tests.

    This fixture uses only PostgreSQL environment variables to configure
    the database connection. If environment variables are not set,
    it will use default values.

    Returns:
        DBConfig object containing database configuration.
    """
    return DBConfig(
        dbname=psycopg_toolbox_db_name,
        user=os.getenv("PGUSER", "postgres"),
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        password=os.getenv(
            "PGPASSWORD", None
        ),  # rely on trust authentication if not found
    )


@pytest.fixture
async def psycopg_toolbox_empty_db(
    psycopg_toolbox_db_name: str,
    db_config: DBConfig,
    *,
    dbname: str | None = None,
    encoding: str | None = None,
    template: str | None = None,
) -> AsyncGenerator[LoggingConnection, None]:
    """Create a temporary test database and provide a connection to it.

    This fixture:
    1. Creates a new database for testing
    2. Provides a connection to that database
    3. Drops the database after the test

    Args:
        psycopg_toolbox_db_name: The default database name from the psycopg_toolbox_db_name fixture
        db_config: Database configuration for the connection
        dbname: Optional name for the test database. If not provided,
               will use the name from psycopg_toolbox_db_name fixture
        encoding: Optional character encoding for the database
        template: Optional template database to use

    Yields:
        An AsyncConnection to the test database
    """
    # Use provided dbname or the one from the fixture
    dbname = dbname or psycopg_toolbox_db_name

    # Connect to default database to create/drop test database
    async with await LoggingConnection.connect(
        dbname="postgres",
        user=db_config.user,
        password=db_config.password,
        host=db_config.host,
        port=db_config.port,
    ) as conn:
        # Create the test database
        await create_database(
            conn, dbname, encoding=encoding, template=template, ignore_exists=True
        )

        # Connect to the test database
        async with await LoggingConnection.connect(
            dbname=dbname,
            user=db_config.user,
            password=db_config.password,
            host=db_config.host,
            port=db_config.port,
        ) as test_conn:
            yield test_conn

        # Drop the test database
        await drop_database(conn, dbname, ignore_missing=True)
