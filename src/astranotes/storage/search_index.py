"""SearchIndex: FTS5-backed full-text search over note title and body (FR-4).

Locked notes are kept out of the index entirely, so their content is not
discoverable while encrypted. User queries are tokenized before they reach the
FTS5 MATCH parser, which neutralizes the empty-query and special-character edge
cases the Week 3.1 refinement called out for FR-03 (e.g. a stray apostrophe no
longer breaks the parser).
"""

import re


class SearchIndex:
    def __init__(self, storage) -> None:
        self._storage = storage

    def index(self, note) -> None:
        """(Re)index a note. Locked notes are removed instead of indexed."""
        self.remove(note.note_id)
        if note.is_locked:
            return
        self._storage.execute(
            "INSERT INTO notes_fts (note_id, title, content) VALUES (?, ?, ?)",
            (note.note_id, note.title, note.content),
        )

    def remove(self, note_id: str) -> None:
        self._storage.execute("DELETE FROM notes_fts WHERE note_id = ?", (note_id,))

    def search(self, query: str) -> list[dict]:
        """Return [{note_id, snippet}] ranked by relevance. An empty or
        all-symbol query returns no rows (the caller decides what to show)."""
        match = self._to_match(query)
        if match is None:
            return []
        return self._storage.query(
            "SELECT note_id, snippet(notes_fts, 2, '[', ']', '…', 12) AS snippet "
            "FROM notes_fts WHERE notes_fts MATCH ? ORDER BY rank",
            (match,),
        )

    @staticmethod
    def _to_match(query: str) -> str | None:
        """Turn raw user input into a safe prefix query, or None if it has no
        searchable tokens."""
        tokens = re.findall(r"\w+", (query or "").lower())
        if not tokens:
            return None
        return " ".join(f"{token}*" for token in tokens)
