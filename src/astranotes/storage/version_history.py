"""VersionHistory: append-only snapshots of note content.

Aggregated by NoteRepository (the hollow-diamond aggregation in the Week 4.2
class diagram). Snapshots intentionally outlive their note — there is no foreign
key back to `notes` — so a deleted note can still be restored (FR-3 + FR-6).
"""

from uuid import uuid4

from astranotes.timeutil import now_iso


class VersionHistory:
    def __init__(self, storage) -> None:
        self._storage = storage

    def snapshot(self, note) -> None:
        """Record the note's current title and content as a new version (FR-6)."""
        self._storage.execute(
            "INSERT INTO note_versions (version_id, note_id, title_snapshot, content_snapshot, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (str(uuid4()), note.note_id, note.title, note.content, now_iso()),
        )

    def list_for(self, note_id: str) -> list[dict]:
        """Versions for a note, newest first (by insertion order)."""
        return self._storage.query(
            "SELECT version_id, note_id, title_snapshot, content_snapshot, created_at "
            "FROM note_versions WHERE note_id = ? ORDER BY rowid DESC",
            (note_id,),
        )

    def get(self, version_id: str) -> dict | None:
        rows = self._storage.query(
            "SELECT version_id, note_id, title_snapshot, content_snapshot, created_at "
            "FROM note_versions WHERE version_id = ?",
            (version_id,),
        )
        return rows[0] if rows else None
