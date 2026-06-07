"""AuditLog: append-only record of security-sensitive events.

Append-only is enforced by database triggers (see schema.sql); this class only
ever inserts and reads. Lock, unlock, and restore each write one row, giving a
tamper-evident trail — the local-first realization of the original SPR-03
requirement.
"""

from uuid import uuid4

from astranotes.timeutil import now_iso


class AuditLog:
    def __init__(self, storage) -> None:
        self._storage = storage

    def record(self, action: str, target_note_id: str | None = None) -> None:
        self._storage.execute(
            "INSERT INTO audit_log (event_id, action, target_note_id, created_at) VALUES (?, ?, ?, ?)",
            (str(uuid4()), action, target_note_id, now_iso()),
        )

    def all(self) -> list[dict]:
        return self._storage.query(
            "SELECT event_id, action, target_note_id, created_at FROM audit_log ORDER BY rowid DESC"
        )
