"""LocalStorage: dict isolation and graceful failure (NFR-2, ADR-0003)."""

import pytest

from astranotes.errors import StorageError
from astranotes.storage.local_storage import LocalStorage


def test_query_returns_plain_dicts(storage):
    storage.execute(
        "INSERT INTO notes (note_id, title, content, created_at, last_modified) VALUES (?, ?, ?, ?, ?)",
        ("a", "t", "", "2026-01-01", "2026-01-01"),
    )
    rows = storage.query("SELECT * FROM notes")
    assert rows and isinstance(rows[0], dict)


def test_schema_creates_core_tables(storage):
    rows = storage.query("SELECT name FROM sqlite_master WHERE type='table'")
    names = {r["name"] for r in rows}
    assert {"notes", "folders", "tags", "note_tags", "note_versions", "audit_log"} <= names


def test_corrupt_db_raises_storage_error(tmp_path):
    """The failure path is real, not just structural — corrupt the file and
    confirm the next read surfaces a StorageError (the Week 6 audit finding)."""
    db_path = tmp_path / "notes.db"
    storage = LocalStorage(db_path)
    storage.execute(
        "INSERT INTO notes (note_id, title, content, created_at, last_modified) VALUES (?, ?, ?, ?, ?)",
        ("x", "t", "", "2026-01-01", "2026-01-01"),
    )
    db_path.write_bytes(b"this is not a sqlite database file")
    with pytest.raises(StorageError):
        storage.query("SELECT * FROM notes")
