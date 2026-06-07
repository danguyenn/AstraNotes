"""Seed AstraNotes with realistic demo data for the walkthrough.

Run from the project root:  python demo/seed_data.py

Idempotent: if the database already has notes, it leaves them alone. Pass
--reset to wipe and reseed. Uses the same configuration as the running app, so
the dev server (`astranotes`) will show this data immediately.
"""

import pathlib
import sys

# Allow running without an editable install.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from astranotes.config import load_config
from astranotes.services.encryption_service import EncryptionService
from astranotes.services.note_service import NoteService
from astranotes.storage.local_storage import LocalStorage
from astranotes.storage.note_repository import NoteRepository

FOLDERS = ["Work", "Personal", "Research"]

NOTES = [
    {
        "title": "Project Kickoff — AstraNotes",
        "folder": "Work",
        "tags": ["work", "planning"],
        "content": (
            "## Agenda\n"
            "- Confirm **local-first** scope (Flask + SQLite)\n"
            "- Walk the layered architecture\n"
            "- Demo the secure-notes flow\n\n"
            "> The cloud vision (Supabase) is the documented roadmap, not the build.\n"
        ),
    },
    {
        "title": "Architecture Cheat Sheet",
        "folder": "Work",
        "tags": ["work", "design"],
        "content": (
            "Imports point **down only**: `web -> services -> storage -> domain`.\n\n"
            "- `LocalStorage` is the only module that imports `sqlite3`\n"
            "- Validation lives in the `Note` constructor\n"
            "- `VersionHistory` survives note deletion (no FK)\n"
        ),
    },
    {
        "title": "Reading List",
        "folder": "Personal",
        "tags": ["personal", "reading"],
        "content": "- Designing Data-Intensive Applications\n- The Pragmatic Programmer\n- A Philosophy of Software Design\n",
    },
    {
        "title": "Weekend Trip Plan",
        "folder": "Personal",
        "tags": ["personal"],
        "content": "Pack light. Markdown export test: `Q3 / Budget & Forecast` (filename gets sanitized).\n",
    },
    {
        "title": "FTS5 vs tsvector — notes",
        "folder": "Research",
        "tags": ["research", "search"],
        "content": (
            "SQLite **FTS5** gives ranked full-text search with snippets, fully local.\n"
            "Postgres `tsvector` has richer weighting — the trade we accepted on the pivot.\n"
        ),
    },
    {
        "title": "Encryption design",
        "folder": "Research",
        "tags": ["research", "security"],
        "content": "Fernet = AES-128-CBC + HMAC. Key stays outside the DB. Locked notes are ciphertext at rest.\n",
    },
]

# Becomes a locked SecureNote after creation.
SECRET = {
    "title": "API Keys (private)",
    "folder": "Work",
    "tags": ["work", "secret"],
    "content": "PROVIDER_TOKEN = sk-demo-not-a-real-key-1234567890\nNotes: rotate quarterly.\n",
}


def _wipe(storage):
    for table in ("note_tags", "note_versions", "notes_fts", "notes", "tags", "folders"):
        try:
            storage.execute(f"DELETE FROM {table}")
        except Exception:
            pass


def main(reset: bool = False) -> None:
    cfg = load_config()
    storage = LocalStorage(cfg.db_path)
    repo = NoteRepository(storage)
    service = NoteService(repo, EncryptionService(cfg.encryption_key))

    if reset:
        _wipe(storage)
    elif service.list_notes():
        print("Database already has notes — nothing to do. Use --reset to reseed.")
        return

    folder_ids = {}
    for name in FOLDERS:
        try:
            folder_ids[name] = repo.create_folder(name)
        except ValueError:
            match = [f for f in repo.list_folders() if f["name"] == name]
            folder_ids[name] = match[0]["folder_id"] if match else None

    for note in NOTES:
        service.create_note(
            note["title"], note["content"], folder_id=folder_ids.get(note["folder"]), tags=note["tags"]
        )

    secret = service.create_note(
        SECRET["title"], SECRET["content"], folder_id=folder_ids.get(SECRET["folder"]), tags=SECRET["tags"]
    )
    service.make_private(secret.note_id)  # encrypt at rest + record an audit event

    print(f"Seeded {len(NOTES) + 1} notes (1 locked) across {len(FOLDERS)} folders at {cfg.db_path}")


if __name__ == "__main__":
    main(reset="--reset" in sys.argv)
