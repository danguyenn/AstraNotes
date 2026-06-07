"""NoteRepository: domain-shaped persistence.

Translates between Note objects and database rows, and owns the two secondary
storage concerns from the class diagram: VersionHistory and SearchIndex.

Write ordering follows the failure principle from the Architecture Decision Log
(ADR-0006, carried from the original Supabase design): the primary write to the
`notes` table commits first; the secondary writes (version snapshot, search
index, tags) follow and are never allowed to roll back the primary write. A
failure recording a version must not lose the user's note.
"""

from datetime import datetime
from uuid import uuid4

from astranotes.domain.note import Note, SecureNote
from astranotes.errors import NoteNotFoundError
from astranotes.storage.audit_log import AuditLog
from astranotes.storage.search_index import SearchIndex
from astranotes.storage.version_history import VersionHistory
from astranotes.timeutil import utcnow


def _iso(value) -> str:
    return value.isoformat() if isinstance(value, datetime) else str(value)


def _parse(value) -> datetime:
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return utcnow()


class NoteRepository:
    def __init__(self, storage) -> None:
        self._storage = storage
        self.versions = VersionHistory(storage)
        self.search = SearchIndex(storage)
        self.audit = AuditLog(storage)

    # --- notes -----------------------------------------------------------
    def save(self, note: Note) -> Note:
        """Insert or update a note, then snapshot, index, and persist its tags."""
        note.last_modified = utcnow()
        exists = self._storage.query("SELECT note_id FROM notes WHERE note_id = ?", (note.note_id,))
        row = (
            note.title,
            note.content,
            note.folder_id,
            1 if note.is_locked else 0,
            note.encryption_key_ref,
            _iso(note.created_at),
            _iso(note.last_modified),
            note.note_id,
        )
        if exists:
            self._storage.execute(
                "UPDATE notes SET title=?, content=?, folder_id=?, is_locked=?, "
                "encryption_key_ref=?, created_at=?, last_modified=? WHERE note_id=?",
                row,
            )
        else:
            self._storage.execute(
                "INSERT INTO notes (title, content, folder_id, is_locked, encryption_key_ref, "
                "created_at, last_modified, note_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                row,
            )
        # Secondary concerns — order matters, see module docstring.
        self.versions.snapshot(note)
        self.search.index(note)
        self._save_tags(note)
        return note

    def get(self, note_id: str) -> Note | None:
        rows = self._storage.query("SELECT * FROM notes WHERE note_id = ?", (note_id,))
        return self._row_to_note(rows[0]) if rows else None

    def load_all(self, folder_id: str | None = None, tag: str | None = None) -> list[Note]:
        """Every note, most-recently-modified first, optionally filtered by
        folder and/or tag (FR-7)."""
        if tag:
            sql = (
                "SELECT n.* FROM notes n "
                "JOIN note_tags nt ON n.note_id = nt.note_id "
                "JOIN tags t ON nt.tag_id = t.tag_id WHERE t.name = ?"
            )
            params: list = [tag]
            if folder_id is not None:
                sql += " AND n.folder_id = ?"
                params.append(folder_id)
        else:
            sql = "SELECT * FROM notes"
            params = []
            if folder_id is not None:
                sql += " WHERE folder_id = ?"
                params.append(folder_id)
        sql += " ORDER BY last_modified DESC"
        return [self._row_to_note(r) for r in self._storage.query(sql, tuple(params))]

    def delete(self, note_id: str) -> None:
        """Delete a note and its search-index entry. Version history is kept on
        purpose so the note can be restored later (FR-3 + FR-6)."""
        if self.get(note_id) is None:
            raise NoteNotFoundError(f"No note with id {note_id!r}.")
        # note_tags has no FK to notes, so clean up the join rows explicitly.
        self._storage.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))
        self._storage.execute("DELETE FROM notes WHERE note_id = ?", (note_id,))
        self.search.remove(note_id)

    def _row_to_note(self, row: dict) -> Note:
        cls = SecureNote if row["is_locked"] else Note
        return cls(
            title=row["title"],
            content=row["content"],
            note_id=row["note_id"],
            folder_id=row["folder_id"],
            tags=self._tags_for(row["note_id"]),
            is_locked=bool(row["is_locked"]),
            encryption_key_ref=row["encryption_key_ref"],
            created_at=_parse(row["created_at"]),
            last_modified=_parse(row["last_modified"]),
        )

    # --- tags ------------------------------------------------------------
    def _save_tags(self, note: Note) -> None:
        self._storage.execute("DELETE FROM note_tags WHERE note_id = ?", (note.note_id,))
        for raw in note.tags:
            name = raw.strip()
            if not name:
                continue
            found = self._storage.query("SELECT tag_id FROM tags WHERE name = ?", (name,))
            if found:
                tag_id = found[0]["tag_id"]
            else:
                tag_id = str(uuid4())
                self._storage.execute(
                    "INSERT INTO tags (tag_id, name) VALUES (?, ?)", (tag_id, name)
                )
            self._storage.execute(
                "INSERT OR IGNORE INTO note_tags (note_id, tag_id) VALUES (?, ?)",
                (note.note_id, tag_id),
            )

    def _tags_for(self, note_id: str) -> list[str]:
        rows = self._storage.query(
            "SELECT t.name FROM tags t JOIN note_tags nt ON t.tag_id = nt.tag_id "
            "WHERE nt.note_id = ? ORDER BY t.name",
            (note_id,),
        )
        return [r["name"] for r in rows]

    def list_tags(self) -> list[str]:
        rows = self._storage.query("SELECT DISTINCT name FROM tags ORDER BY name")
        return [r["name"] for r in rows]

    # --- folders ---------------------------------------------------------
    def list_folders(self) -> list[dict]:
        return self._storage.query(
            "SELECT f.folder_id, f.name, "
            "(SELECT COUNT(*) FROM notes n WHERE n.folder_id = f.folder_id) AS note_count "
            "FROM folders f ORDER BY f.name"
        )

    def create_folder(self, name: str) -> str:
        name = (name or "").strip()
        if not name:
            raise ValueError("Folder name must be a non-empty string.")
        if self._storage.query("SELECT folder_id FROM folders WHERE name = ?", (name,)):
            raise ValueError(f"A folder named {name!r} already exists.")
        folder_id = str(uuid4())
        self._storage.execute(
            "INSERT INTO folders (folder_id, name) VALUES (?, ?)", (folder_id, name)
        )
        return folder_id

    def get_folder(self, folder_id: str) -> dict | None:
        rows = self._storage.query(
            "SELECT folder_id, name FROM folders WHERE folder_id = ?", (folder_id,)
        )
        return rows[0] if rows else None
