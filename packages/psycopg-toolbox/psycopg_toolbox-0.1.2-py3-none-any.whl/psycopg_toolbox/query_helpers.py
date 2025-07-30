"""Query helper functions for psycopg-toolbox."""

from psycopg import AsyncConnection
from psycopg.sql import SQL, Identifier

from .contextmanagers import autocommit
from .exceptions import AlreadyExistsError


async def database_exists(conn: AsyncConnection, dbname: str) -> bool:
    """Check if a database exists.

    Args:
        conn: Connection to use for checking
        dbname: Name of the database to check

    Returns:
        True if the database exists, False otherwise
    """
    exists = await conn.execute(
        SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [dbname]
    )
    return bool(await exists.fetchone())


async def create_database(
    conn: AsyncConnection,
    dbname: str,
    *,
    encoding: str | None = None,
    template: str | None = None,
    ignore_exists: bool = False,
    owner: str | None = None,
) -> bool:
    """Create a new PostgreSQL database.

    Args:
        conn: Connection to use for creating the database
        dbname: Name of the database to create
        encoding: Optional character encoding for the database
        template: Optional template database to use
        ignore_exists: If True, silently ignore if database already exists
        owner: Optional role name to set as the owner of the database
    Raises:
        AlreadyExistsError: If database already exists and ignore_exists is False
        psycopg.Error: If database creation fails for other reasons
    Returns:
        True if a new database was created, False if the database already existed
        and ignore_exists was True
    """
    async with autocommit(conn):
        # Check if database exists
        if await database_exists(conn, dbname):
            if ignore_exists:
                return False
            raise AlreadyExistsError(f"Database {dbname} already exists")

        # Build the CREATE DATABASE statement
        query = SQL("CREATE DATABASE {} ").format(Identifier(dbname))
        if encoding:
            query += SQL("ENCODING {} ").format(SQL(encoding))
        if template:
            query += SQL("TEMPLATE {} ").format(Identifier(template))
        if owner:
            query += SQL("OWNER {} ").format(Identifier(owner))

        await conn.execute(query)
        return True


async def drop_database(
    conn: AsyncConnection,
    dbname: str,
    *,
    ignore_missing: bool = False,
) -> None:
    """Drop a PostgreSQL database.

    This function will:
    1. Terminate all connections to the database
    2. Drop the database

    Args:
        conn: Connection to use for dropping the database
        dbname: Name of the database to drop
        ignore_missing: If True, silently ignore if database doesn't exist
    Raises:
        psycopg.Error: If database drop fails for reasons other than missing database
    Returns:
        True if the database was dropped, False if the database didn't exist
        and ignore_missing was True
    """
    async with autocommit(conn):
        # Terminate all connections to the database
        await conn.execute(
            SQL(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s
                AND pid <> pg_backend_pid()
            """
            ),
            [dbname],
        )

        if not ignore_missing:
            sql = "DROP DATABASE {}"
        else:
            sql = "DROP DATABASE IF EXISTS {}"
        await conn.execute(SQL(sql).format(Identifier(dbname)))


async def schema_exists(conn: AsyncConnection, schema_name: str) -> bool:
    """Check if a schema exists.

    Args:
        conn: Connection to use for checking
        schema_name: Name of the schema to check

    Returns:
        True if the schema exists, False otherwise
    """
    exists = await conn.execute(
        SQL("SELECT 1 FROM pg_namespace WHERE nspname = %s"), [schema_name]
    )
    return bool(await exists.fetchone())


async def create_schema(
    conn: AsyncConnection,
    schema_name: str,
    *,
    owner: str | None = None,
    ignore_exists: bool = False,
) -> bool:
    """Create a new PostgreSQL schema.

    Args:
        conn: Connection to use for creating the schema
        schema_name: Name of the schema to create
        owner: Optional role name to set as the owner of the schema
        ignore_exists: If True, silently ignore if schema already exists

    Raises:
        AlreadyExistsError: If schema already exists and ignore_exists is False
        psycopg.Error: If schema creation fails for other reasons

    Returns:
        True if a new schema was created, False if the schema already existed
        and ignore_exists was True
    """
    # Check if schema exists
    if await schema_exists(conn, schema_name):
        if ignore_exists:
            return False
        raise AlreadyExistsError(f"Schema {schema_name} already exists")

    # Build the CREATE SCHEMA statement
    query = SQL("CREATE SCHEMA {} ").format(Identifier(schema_name))
    if owner:
        query += SQL("AUTHORIZATION {} ").format(Identifier(owner))

    await conn.execute(query)
    return True


async def drop_schema(
    conn: AsyncConnection,
    schema_name: str,
    *,
    ignore_missing: bool = False,
    cascade: bool = False,
) -> None:
    """Drop a PostgreSQL schema.

    Args:
        conn: Connection to use for dropping the schema
        schema_name: Name of the schema to drop
        ignore_missing: If True, silently ignore if schema doesn't exist
        cascade: If True, automatically drop objects (tables, functions, etc.)
                that are contained in the schema

    Raises:
        psycopg.Error: If schema drop fails for reasons other than missing schema
    """
    if not ignore_missing:
        sql = "DROP SCHEMA {}"
    else:
        sql = "DROP SCHEMA IF EXISTS {}"

    if cascade:
        sql += " CASCADE"

    await conn.execute(SQL(sql).format(Identifier(schema_name)))
