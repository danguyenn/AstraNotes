"""LocalStorage: the single point of contact with SQLite.

This is the only module in the codebase that imports `sqlite3`. Every error is
re-raised as a domain-level StorageError, and every read returns plain dicts
rather than `sqlite3.Row`, so nothing above the storage layer depends on the
database driver. (This boundary was the bug the Week 6 quality audit caught:
`query()` had been leaking `sqlite3.Row`, which silently coupled the repository
to the driver. See ADR-0003.)

Connections are opened and closed per call. Closing eagerly matters on Windows,
where a lingering handle keeps the database file locked.
"""

import sqlite3
from importlib import resources
from pathlib import Path

from astranotes.errors import StorageError


class LocalStorage:
    def __init__(self, db_path) -> None:
        self._db_path = str(db_path)
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self) -> None:
        schema = (
            resources.files("astranotes.storage").joinpath("schema.sql").read_text(encoding="utf-8")
        )
        conn = None
        try:
            conn = self._connect()
            conn.executescript(schema)
            conn.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"Failed to initialize database schema: {exc}") from exc
        finally:
            if conn is not None:
                conn.close()

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        """Run a SELECT and return rows as plain dicts."""
        conn = None
        try:
            conn = self._connect()
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]
        except sqlite3.Error as exc:
            raise StorageError(str(exc)) from exc
        finally:
            if conn is not None:
                conn.close()

    def execute(self, sql: str, params: tuple = ()) -> None:
        """Run a single write statement and commit it."""
        conn = None
        try:
            conn = self._connect()
            conn.execute(sql, params)
            conn.commit()
        except sqlite3.Error as exc:
            raise StorageError(str(exc)) from exc
        finally:
            if conn is not None:
                conn.close()
