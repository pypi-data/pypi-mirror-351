"""Context managers for psycopg-toolbox."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from psycopg import AsyncConnection


@asynccontextmanager
async def autocommit(conn: AsyncConnection) -> AsyncGenerator[AsyncConnection, None]:
    """Temporarily set a connection to autocommit mode.

    Args:
        conn: The connection to modify
    Yields:
        The connection in autocommit mode
    """
    original_autocommit = conn.autocommit
    try:
        await conn.set_autocommit(True)
        yield conn
    finally:
        await conn.set_autocommit(original_autocommit)


@asynccontextmanager
async def switch_role(conn: AsyncConnection, role: str) -> AsyncGenerator[str, None]:
    """Temporarily switch the database role for a connection.

    Args:
        conn: The connection to modify
        role: The role to switch to
    Yields:
        The previous role name
    """
    # Get current role
    result = await conn.execute("SELECT current_user")
    row = await result.fetchone()
    if row is None:
        raise RuntimeError("Failed to get current user")
    original_role = row[0]

    try:
        # Switch to new role
        await conn.execute(f"SET ROLE {role}")
        yield original_role
    finally:
        # Restore original role
        await conn.execute(f"SET ROLE {original_role}")


@asynccontextmanager
async def obtain_advisory_lock(
    conn: AsyncConnection, lock_name: str, blocking: bool = True
) -> AsyncGenerator[bool, None]:
    """Temporarily obtain an advisory lock.

    Args:
        conn: The connection to use
        lock_name: The name of the lock to obtain
        blocking: Whether to wait for the lock (True) or return immediately (False)
    Yields:
        True if the lock was obtained, False if not (only in non-blocking mode)
    """
    obtained = False
    try:
        if blocking:
            await conn.execute(
                "SELECT pg_advisory_lock(hashtext(%s)::bigint)", (lock_name,)
            )
            obtained = True
            yield obtained
        else:
            result = await conn.execute(
                "SELECT pg_try_advisory_lock(hashtext(%s)::bigint)", (lock_name,)
            )
            row = await result.fetchone()
            if row is None:
                raise RuntimeError("Failed to obtain lock")
            obtained = row[0]
            yield obtained
    finally:
        if blocking or (not blocking and obtained):
            await conn.execute(
                "SELECT pg_advisory_unlock(hashtext(%s)::bigint)", (lock_name,)
            )
