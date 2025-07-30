"""Query helper functions for managing PostgreSQL roles and users."""

import logging
from typing import Any

from psycopg import AsyncConnection
from psycopg.sql import SQL, Identifier, Literal, Composable

from .exceptions import AlreadyExistsError

logger = logging.getLogger(__name__)


def _get_value(row: dict | tuple, key: str | int) -> Any:
    """Get a value from a row, handling both dict and tuple row types.

    Args:
        row: The row to get the value from
        key: The key/index to get the value for

    Returns:
        The value from the row
    """
    if isinstance(row, dict):
        return row[key]
    return row[0]


async def user_or_role_exists(conn: AsyncConnection, username: str) -> bool:
    """Check if a user or role exists.

    Args:
        conn: The connection to use
        username: The username/role name to check

    Returns:
        True if the user/role exists, False otherwise
    """
    result = await conn.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", [username])
    return (await result.fetchone()) is not None


async def create_user(
    *,
    conn: AsyncConnection,
    name: str,
    password: str | None = None,
    parent_role: str | None = None,
    error_if_exists: bool = True,
) -> None:
    """Create an application database user.

    Args:
        conn: The connection to use
        name: The username to create
        password: Optional password for the user
        parent_role: Optional role to inherit from
        error_if_exists: Whether to raise an error if the user exists

    Raises:
        AlreadyExistsError: If the user exists and error_if_exists is True
    """
    await _create_user_or_role(
        conn,
        name=name,
        password=password,
        parent_role=parent_role,
        error_if_exists=error_if_exists,
        is_user=True,
    )


async def create_role(
    *,
    conn: AsyncConnection,
    name: str,
    parent_role: str | None = None,
    error_if_exists: bool = True,
) -> None:
    """Create an application database role.

    Args:
        conn: The connection to use
        name: The role name to create
        parent_role: Optional role to inherit from
        error_if_exists: Whether to raise an error if the role exists

    Raises:
        AlreadyExistsError: If the role exists and error_if_exists is True
    """
    await _create_user_or_role(
        conn,
        name=name,
        password=None,
        parent_role=parent_role,
        error_if_exists=error_if_exists,
        is_user=False,
    )


async def _create_user_or_role(
    conn: AsyncConnection,
    *,
    name: str,
    password: str | None,
    parent_role: str | None,
    error_if_exists: bool,
    is_user: bool,
) -> None:
    """Shared function used by create_role/create_user.

    Args:
        conn: The connection to use
        name: The role/user name to create
        password: Optional password for users
        parent_role: Optional role to inherit from
        error_if_exists: Whether to raise an error if exists
        is_user: Whether this is a user (True) or role (False)

    Raises:
        AlreadyExistsError: If the role/user exists and error_if_exists is True
    """
    if await user_or_role_exists(conn, name):
        if error_if_exists:
            raise AlreadyExistsError(f"Role/user {name} already exists in DB.")
        else:
            logger.info("Skipping creation of role/user %s (already exists)", name)
            return

    # Build credentials SQL
    if is_user:
        if password is None:
            creds_sql: Composable = SQL("LOGIN")
        else:
            creds_sql = SQL("LOGIN ENCRYPTED PASSWORD {passwd}").format(
                passwd=Literal(password)
            )
    else:
        creds_sql = SQL("NOLOGIN")

    # Build inherited role SQL
    if parent_role is None or parent_role == name:
        inherited_role_sql: Composable = SQL("")
    else:
        inherited_role_sql = SQL("IN ROLE {parent_role}").format(
            parent_role=Identifier(parent_role)
        )

    # Create the role/user
    await conn.execute(
        SQL("CREATE ROLE {rolename} {creds_sql} {inherited_role_sql}").format(
            rolename=Identifier(name),
            creds_sql=creds_sql,
            inherited_role_sql=inherited_role_sql,
        )
    )


async def drop_user_or_role(
    conn: AsyncConnection, rolename: str, ignore_missing: bool = False
) -> None:
    """Delete an application database user or role.

    Args:
        conn: The connection to use
        rolename: The role/user name to drop
        ignore_missing: Whether to ignore if the role/user doesn't exist
    """
    if not ignore_missing:
        sql = "DROP ROLE {rolename}"
    else:
        sql = "DROP ROLE IF EXISTS {rolename}"
    await conn.execute(SQL(sql).format(rolename=Identifier(rolename)))


async def get_current_user(conn: AsyncConnection) -> str:
    """Get the current database username.

    Args:
        conn: The connection to use

    Returns:
        The current database username
    """
    result = await conn.execute("SELECT CURRENT_USER AS user")
    row = await result.fetchone()
    assert row is not None
    return _get_value(row, "user")
