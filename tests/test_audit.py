"""Append-only audit log (SEC / SPR-03 echo)."""

import pytest

from astranotes.errors import StorageError
from astranotes.storage.audit_log import AuditLog


def test_record_and_read(storage):
    audit = AuditLog(storage)
    audit.record("lock", "note-1")
    events = audit.all()
    assert len(events) == 1 and events[0]["action"] == "lock"


def test_update_is_rejected(storage):
    audit = AuditLog(storage)
    audit.record("lock", "note-1")
    with pytest.raises(StorageError):
        storage.execute("UPDATE audit_log SET action = 'tampered'")


def test_delete_is_rejected(storage):
    audit = AuditLog(storage)
    audit.record("lock", "note-1")
    with pytest.raises(StorageError):
        storage.execute("DELETE FROM audit_log")


def test_lock_and_restore_record_events(service):
    note = service.create_note("Title", "body")
    service.make_private(note.note_id)
    versions = service.list_versions(note.note_id)
    service.restore_version(note.note_id, versions[-1]["version_id"])
    actions = [e["action"] for e in service.audit_events()]
    assert "lock" in actions and "restore" in actions
