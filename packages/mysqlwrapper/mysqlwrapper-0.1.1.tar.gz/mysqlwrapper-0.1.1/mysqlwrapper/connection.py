"""
Handles connection logic and database credentials for PyMySQL.
"""

import pymysql
from typing import Optional


# Internal global store for DB credentials
_db_credentials: dict[str, Optional[str]] = {
    "user": None,
    "password": None,
    "database": None,
    "host": None,
}


def db_credentials(user: str, password: str, database: str, host: str) -> None:
    """
    Set database credentials programmatically.

    Args:
        user (str): Database username.
        password (str): Database password.
        database (str): Name of the target database.
        host (str): Hostname or IP address of the database server.

    Example:
        db_credentials(
            user="admin",
            password="mypassword",
            database="mydb",
            host="localhost"
        )
    """
    _db_credentials["user"] = user
    _db_credentials["password"] = password
    _db_credentials["database"] = database
    _db_credentials["host"] = host


def db_connect():
    """
    Establishes a connection to the database using previously set credentials.

    Returns:
        pymysql.connections.Connection: A connection object with autocommit enabled.

    Raises:
        ValueError: If credentials have not been set via `db_credentials`.

    Example:
        conn = db_connect()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
    """
    if None in _db_credentials.values():
        raise ValueError("Database credentials are not fully set. Call db_credentials() first.")

    conn = pymysql.connect(
        host=_db_credentials["host"],
        port=3306,
        user=_db_credentials["user"],
        password=_db_credentials["password"],
        db=_db_credentials["database"],
        autocommit=True
    )
    return conn