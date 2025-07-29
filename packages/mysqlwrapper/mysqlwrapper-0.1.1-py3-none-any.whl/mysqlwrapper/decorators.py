"""
Provides decorators to automatically handle database cursors for both sync and async functions.
"""

import functools
from .connection import db_connect


def ensure_cursor(func):
    """
    Decorator to ensure a database cursor is available to the function.

    If a `cursor` keyword argument is not passed, it will create a new connection and cursor.
    This is ideal for synchronous functions that require DB access.

    Example:
        @ensure_cursor
        def get_users(*, cursor):
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cursor = kwargs.get('cursor')
        if cursor:
            return func(*args, **kwargs)

        # Establish connection and create cursor
        with db_connect() as conn:
            cursor = conn.cursor()
            kwargs['cursor'] = cursor
            return func(*args, **kwargs)

    return wrapper


def async_ensure_cursor(func):
    """
    Async version of ensure_cursor. Ensures an async function receives a `cursor`.

    NOTE: While PyMySQL does not support true async I/O, this can be useful for
    coroutine-based designs with blocking I/O.

    Example:
        @async_ensure_cursor
        async def fetch(*, cursor):
            cursor.execute("SELECT * FROM data")
            return cursor.fetchall()
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        cursor = kwargs.get('cursor')
        if cursor:
            return await func(*args, **kwargs)

        # Establish connection and create cursor
        with db_connect() as conn:
            cursor = conn.cursor()
            kwargs['cursor'] = cursor
            return await func(*args, **kwargs)

    return wrapper