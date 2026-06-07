"""NoteService use-case orchestration (FR-1, FR-2, FR-3, FR-5, FR-7)."""

import pytest

from astranotes.errors import NoteNotFoundError
from astranotes.services.session import UserSession


def test_create_and_get(service):
    note = service.create_note("Title", "body", tags=["t"])
    assert service.get_note(note.note_id).title == "Title"


def test_edit_note(service):
    note = service.create_note("Title", "body")
    service.edit_note(note.note_id, "New", "new body")
    loaded = service.get_note(note.note_id)
    assert (loaded.title, loaded.content) == ("New", "new body")


def test_edit_missing_raises(service):
    with pytest.raises(NoteNotFoundError):
        service.edit_note("ghost", "t", "b")


def test_delete_note(service):
    note = service.create_note("Title", "body")
    service.delete_note(note.note_id)
    assert service.get_note(note.note_id) is None


def test_list_notes(service):
    service.create_note("A")
    service.create_note("B")
    assert len(service.list_notes()) == 2


def test_make_private_encrypts_and_locks(service, repo):
    note = service.create_note("Title", "plaintext body")
    secure = service.make_private(note.note_id)
    assert secure.is_locked
    raw = repo.get(note.note_id)
    assert raw.content != "plaintext body"  # ciphertext at rest


def test_make_public_decrypts(service):
    note = service.create_note("Title", "plaintext body")
    service.make_private(note.note_id)
    public = service.make_public(note.note_id)
    assert public.is_locked is False
    assert public.content == "plaintext body"


def test_reveal_locked_requires_unlocked_session(service):
    note = service.create_note("Title", "plaintext body")
    service.make_private(note.note_id)
    locked = service.get_note(note.note_id)
    assert service.reveal(locked, UserSession(unlocked=False)) is None
    assert service.reveal(locked, UserSession(unlocked=True)) == "plaintext body"


def test_edit_locked_note_reencrypts(service, repo):
    note = service.create_note("Title", "body")
    service.make_private(note.note_id)
    service.edit_note(note.note_id, "Title", "edited secret")
    raw = repo.get(note.note_id)
    assert raw.is_locked and raw.content != "edited secret"
    assert service.reveal(raw, UserSession(unlocked=True)) == "edited secret"


def test_move_note(service):
    fid = service.create_folder("Work")
    note = service.create_note("Title")
    service.move_note(note.note_id, fid)
    assert service.get_note(note.note_id).folder_id == fid
