"""Domain invariants (FR-1)."""

import pytest

from astranotes.domain.note import DEFAULT_KEY_REF, Note, SecureNote


def test_note_requires_non_empty_title():
    with pytest.raises(ValueError):
        Note(title="", content="x")
    with pytest.raises(ValueError):
        Note(title="   ", content="x")


def test_note_trims_title():
    assert Note(title="  Hello  ", content="x").title == "Hello"


def test_note_content_must_be_string():
    with pytest.raises(ValueError):
        Note(title="ok", content=123)  # type: ignore[arg-type]


def test_note_has_id_and_timestamps():
    note = Note(title="t")
    assert note.note_id
    assert note.created_at and note.last_modified
    assert note.is_locked is False


def test_update_content_changes_and_bumps_modified():
    note = Note(title="t", content="a")
    before = note.last_modified
    note.update_content("t2", "b")
    assert (note.title, note.content) == ("t2", "b")
    assert note.last_modified >= before


def test_update_content_rejects_empty_title():
    note = Note(title="t", content="a")
    with pytest.raises(ValueError):
        note.update_content("  ", "b")


def test_securenote_is_locked_with_key_ref():
    secure = SecureNote(title="secret", content="cipher")
    assert secure.is_locked is True
    assert secure.encryption_key_ref == DEFAULT_KEY_REF
