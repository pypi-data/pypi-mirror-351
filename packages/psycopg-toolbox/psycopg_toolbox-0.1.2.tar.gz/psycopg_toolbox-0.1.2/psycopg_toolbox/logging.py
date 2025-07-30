"""Logging implementations for psycopg-toolbox.

This module provides LoggingConnection and LoggingCursor classes that extend psycopg's
AsyncConnection and AsyncCursor to log database operations. The LoggingCursor logs all
executed queries and their parameters, but skips logging parameters if the query contains
sensitive words. The LoggingConnection logs when connections are created and closed, and
uses LoggingCursor as the default cursor_factory.
"""

import logging
import re
from typing import Any, Generic, Self, TypeVar
from collections.abc import Iterable, Mapping, Sequence

from psycopg import AsyncConnection
from psycopg.cursor_async import AsyncCursor
from psycopg.rows import AsyncRowFactory, Row
from psycopg.sql import SQL, Composed

logger = logging.getLogger(__name__)

T = TypeVar("T")


class LoggingCursor(AsyncCursor[T], Generic[T]):
    """A cursor that logs queries and parameters, but skips params if query is sensitive.

    If the query contains a banned word (e.g., password, ssn, credit card),
    parameters are not logged at all.
    """

    # Banned words for sensitive queries
    _BANNED_WORDS = [
        "password",
        "passwd",
        "pwd",
        "token",
        "secret",
        "key",
        "ssn",
        "social security",
        "credit card",
        "cc",
        "card number",
    ]
    _BANNED_WORDS_PATTERN = re.compile(
        r"|".join(re.escape(word) for word in _BANNED_WORDS), re.IGNORECASE
    )

    async def execute(
        self,
        query: str | bytes | SQL | Composed,
        params: Sequence[Any] | Mapping[str, Any] | None = None,
        *,
        prepare: bool | None = None,
        binary: bool | None = None,
    ) -> "LoggingCursor[T]":
        """Execute a query and log it unless it contains sensitive data."""
        logger.info("Executing query: %s", query)
        if params is not None:
            if self._BANNED_WORDS_PATTERN.search(str(query)):
                logger.info("Parameters not logged due to sensitive query.")
            else:
                logger.info("With parameters: %s", params)
        return await super().execute(query, params, prepare=prepare, binary=binary)

    async def executemany(
        self,
        query: str | bytes | SQL | Composed,
        params_seq: Iterable[Sequence[Any] | Mapping[str, Any]],
        *,
        returning: bool = False,
    ) -> None:
        """Execute a query multiple times and log it unless it contains sensitive data."""
        logger.info("Executing query multiple times: %s", query)
        if params_seq is not None:
            if self._BANNED_WORDS_PATTERN.search(str(query)):
                logger.info("Parameters sequence not logged due to sensitive query.")
            else:
                logger.info("With parameters sequence: %s", params_seq)
        await super().executemany(query, params_seq, returning=returning)


class LoggingConnection(AsyncConnection[Row]):
    """A connection that logs when it is created and closed, and uses LoggingCursor by default."""

    async def close(self) -> None:
        """Close the connection and log its closure."""
        logger.info("Connection closed: %s:%s", self.info.host, self.info.port)
        await super().close()

    @classmethod
    async def connect(
        cls,
        conninfo: str = "",
        *,
        autocommit: bool = False,
        prepare_threshold: int | None = None,
        context: Any | None = None,
        row_factory: AsyncRowFactory[Row] | None = None,
        cursor_factory: type[AsyncCursor[Row]] | None = None,
        **kwargs: str | int | None,
    ) -> Self:
        """Create a new connection with LoggingCursor as the default cursor_factory.

        Args:
            conninfo: Connection string
            autocommit: Whether to enable autocommit mode
            prepare_threshold: Number of times a query must be executed before it is prepared
            context: Adaptation context (type Any for compatibility)
            row_factory: Factory for creating row objects
            cursor_factory: Factory for creating cursor objects
            **kwargs: Additional connection parameters
        """
        if cursor_factory is None:
            cursor_factory = LoggingCursor[Row]

        conn = await super().connect(
            conninfo=conninfo,
            autocommit=autocommit,
            prepare_threshold=prepare_threshold,
            context=context,
            row_factory=row_factory,
            cursor_factory=cursor_factory,
            **kwargs,
        )

        logger.info("Connection created: %s:%s", conn.info.host, conn.info.port)
        return conn
