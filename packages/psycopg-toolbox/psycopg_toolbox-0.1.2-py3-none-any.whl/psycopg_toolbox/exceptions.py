"""Custom exceptions for psycopg-toolbox."""


class DatabaseError(Exception):
    """Base class for database-related errors."""

    pass


class AlreadyExistsError(DatabaseError):
    """Raised when attempting to create a database, user or role that already exists."""

    pass
