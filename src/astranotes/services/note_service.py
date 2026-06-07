"""NoteService: orchestrates every AstraNotes use case.

Routes call into this service and nothing else on the way down. The service
coordinates the repository, the encryption service, and the user session; it
does not re-validate the title invariant (the domain constructor owns that) and
it does not touch SQLite (the storage layer owns that).
"""

from astranotes.domain.note import DEFAULT_KEY_REF, Note, SecureNote
from astranotes.errors import NoteNotFoundError
from astranotes.timeutil import utcnow

_UNCHANGED = object()


class NoteService:
    def __init__(self, repository, encryption) -> None:
        self._repo = repository
        self._enc = encryption

    # --- create / read / edit / delete (FR-1, FR-2, FR-3) ----------------
    def create_note(self, title, content="", folder_id=None, tags=None) -> Note:
        note = Note(title=title, content=content, folder_id=folder_id, tags=list(tags or []))
        self._repo.save(note)
        return note

    def get_note(self, note_id) -> Note | None:
        return self._repo.get(note_id)

    def list_notes(self, folder_id=None, tag=None) -> list[Note]:
        return self._repo.load_all(folder_id=folder_id, tag=tag)

    def edit_note(self, note_id, title, content, folder_id=_UNCHANGED, tags=_UNCHANGED) -> Note:
        note = self._require(note_id)
        # A locked note stores ciphertext, so re-encrypt the edited body before
        # it is persisted. The editor only ever shows decrypted text when the
        # session is unlocked, so `content` arrives as plaintext here.
        stored = self._enc.encrypt(content) if note.is_locked else content
        note.update_content(title, stored)
        if folder_id is not _UNCHANGED:
            note.folder_id = folder_id or None
        if tags is not _UNCHANGED:
            note.tags = list(tags or [])
        self._repo.save(note)
        return note

    def delete_note(self, note_id) -> None:
        self._repo.delete(note_id)

    # --- search (FR-4) ---------------------------------------------------
    def search_notes(self, query) -> list[dict]:
        """[{note, snippet}] ranked by relevance. Locked notes are excluded by
        the index, so encrypted content never surfaces in results. An empty or
        all-symbol query returns an empty list."""
        results = []
        for hit in self._repo.search.search(query):
            note = self._repo.get(hit["note_id"])
            if note is not None:
                results.append({"note": note, "snippet": hit.get("snippet") or ""})
        return results

    # --- privacy (FR-5) --------------------------------------------------
    def make_private(self, note_id) -> Note:
        note = self._require(note_id)
        if note.is_locked:
            return note
        secure = SecureNote(
            title=note.title,
            content=self._enc.encrypt(note.content),
            note_id=note.note_id,
            folder_id=note.folder_id,
            tags=note.tags,
            encryption_key_ref=DEFAULT_KEY_REF,
            created_at=note.created_at,
        )
        self._repo.save(secure)
        self._repo.audit.record("lock", note_id)
        return secure

    def make_public(self, note_id) -> Note:
        note = self._require(note_id)
        if not note.is_locked:
            return note
        plain = Note(
            title=note.title,
            content=self._enc.decrypt(note.content),
            note_id=note.note_id,
            folder_id=note.folder_id,
            tags=note.tags,
            created_at=note.created_at,
        )
        self._repo.save(plain)
        self._repo.audit.record("unlock", note_id)
        return plain

    def reveal(self, note, session) -> str | None:
        """Display content for a note: its body if visible, or None when the
        note is locked and the session has not been unlocked."""
        if not note.is_locked:
            return note.content
        if session is None or not session.is_unlocked:
            return None
        return self._enc.decrypt(note.content)

    # --- version history (FR-6) ------------------------------------------
    def list_versions(self, note_id) -> list[dict]:
        return self._repo.versions.list_for(note_id)

    def restore_version(self, note_id, version_id) -> Note:
        version = self._repo.versions.get(version_id)
        if version is None or version["note_id"] != note_id:
            raise NoteNotFoundError("No such version for this note.")
        note = self._require(note_id)
        # Write the snapshot back as the current content. save() records this as
        # a new version too, so the restore is itself reversible (FR-6).
        note.title = version["title_snapshot"]
        note.content = version["content_snapshot"]
        note.last_modified = utcnow()
        self._repo.save(note)
        self._repo.audit.record("restore", note_id)
        return note

    # --- folders & tags (FR-7) -------------------------------------------
    def list_folders(self) -> list[dict]:
        return self._repo.list_folders()

    def create_folder(self, name) -> str:
        return self._repo.create_folder(name)

    def get_folder(self, folder_id) -> dict | None:
        return self._repo.get_folder(folder_id)

    def list_tags(self) -> list[str]:
        return self._repo.list_tags()

    def audit_events(self) -> list[dict]:
        return self._repo.audit.all()

    def move_note(self, note_id, folder_id) -> Note:
        note = self._require(note_id)
        note.folder_id = folder_id or None
        self._repo.save(note)
        return note

    def _require(self, note_id) -> Note:
        note = self._repo.get(note_id)
        if note is None:
            raise NoteNotFoundError(f"No note with id {note_id!r}.")
        return note
