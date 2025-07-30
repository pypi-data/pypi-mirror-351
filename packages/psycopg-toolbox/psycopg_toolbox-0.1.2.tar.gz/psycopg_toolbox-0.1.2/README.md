# psycopg-toolbox

> **Note:** This package is designed exclusively for use with async Python code and async psycopg v3 connections.

A collection of useful utilities and context managers for working with psycopg v3, including role switching, advisory locks, autocommit management, and custom exceptions. Designed to make common PostgreSQL operations more convenient and safer in async Python applications.

## Features

- **Role Management**: Create, drop, and manage database users and roles with inheritance support
- **Role Switching**: Safely switch database roles with automatic rollback (async context manager)
- **Advisory Locks**: Easy-to-use async context managers for PostgreSQL advisory locks
- **Autocommit Management**: Convenient control over transaction autocommit state (async context manager)
- **Logging Support**: Enhanced async connection and cursor classes with built-in logging
- **Custom Exceptions**: Easily catch and handle errors like `AlreadyExistsError`
- **Database Management**: Create, drop, and check existence of databases with proper connection handling

## Installation

```bash
pip install psycopg-toolbox
```

## Quick Start (Async Usage Only)

```python
from psycopg_toolbox import (
    autocommit,
    switch_role,
    obtain_advisory_lock,
    LoggingConnection,
    LoggingCursor,
    create_database,
    database_exists,
    drop_database,
    AlreadyExistsError,
    create_user,
    create_role,
    drop_user_or_role,
    get_current_user,
    user_or_role_exists,
)

# All usage must be within async functions and with async psycopg connections

# Example: Catching AlreadyExistsError
try:
    await create_database(conn, "mydb")
except AlreadyExistsError:
    print("Database already exists!")

# Create a connection with logging
conn = await LoggingConnection.connect(
    "postgresql://user:pass@localhost:5432/dbname"
)

# Switch to a different role
async with switch_role(conn, "new_role") as original_role:
    # Do something as new_role
    await conn.execute("SELECT current_user")

# Use advisory locks
async with obtain_advisory_lock(conn, "my_lock", blocking=True) as obtained:
    if obtained:
        # Do something with the lock
        await conn.execute("SELECT 1")

# Temporarily enable autocommit
async with autocommit(conn):
    # Do something with autocommit enabled
    await conn.execute("SELECT 1")
```

## Detailed Examples

### Role Management (Async Only)
```python
from psycopg_toolbox import create_user, create_role, drop_user_or_role, get_current_user

# Create a new user with password
await create_user(conn, "app_user", password="secret123")

# Create a role that inherits from another role
await create_role(conn, "app_role", parent_role="app_user")

# Check if a user/role exists
if await user_or_role_exists(conn, "app_user"):
    print("User exists!")

# Get the current user
current_user = await get_current_user(conn)

# Drop a user or role
await drop_user_or_role(conn, "app_user", ignore_missing=True)
```

### Role Switching (Async Only)
```python
from psycopg_toolbox import switch_role

async with switch_role(conn, "app_user") as original_role:
    # All operations here will be performed as app_user
    await conn.execute("SELECT current_user")  # Returns 'app_user'
# After the context manager exits, the original role is restored
await conn.execute("SELECT current_user")  # Returns original role
```

### Advisory Locks (Async Only)
```python
from psycopg_toolbox import obtain_advisory_lock

# Blocking mode (default)
async with obtain_advisory_lock(conn, "my_lock") as obtained:
    # Will wait until lock is available
    assert obtained  # Always True in blocking mode
    # Do something with the lock
    pass

# Non-blocking mode
async with obtain_advisory_lock(conn, "my_lock", blocking=False) as obtained:
    if obtained:
        # Lock was acquired
        pass
    else:
        # Lock was not available
        pass
```

### Autocommit Management (Async Only)
```python
from psycopg_toolbox import autocommit

async with autocommit(conn):
    # All operations here will be in autocommit mode
    await conn.execute("SELECT 1")
# After the context manager exits, the original autocommit state is restored
```

### Logging Connection (Async Only)
```python
from psycopg_toolbox import LoggingConnection

# Create a connection with logging
conn = await LoggingConnection.connect(
    "postgresql://user:pass@localhost:5432/dbname",
    log_level="DEBUG"  # Optional: set logging level
)

# All SQL operations will be logged
await conn.execute("SELECT 1")
```

### Database Management (Async Only)
```python
from psycopg_toolbox import create_database, drop_database, database_exists

# Create a new database
await create_database(conn, "mydb", encoding="UTF8", owner="app_user")

# Check if database exists
if await database_exists(conn, "mydb"):
    print("Database exists!")

# Drop a database (with connection termination)
await drop_database(conn, "mydb", ignore_missing=True)
```

## Requirements

- Python >= 3.11
- psycopg >= 3.2.9
- **Async usage only**: All features require async/await and async psycopg connections

## License

This project is licensed under the MIT License - see the LICENSE file for details.
