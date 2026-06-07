"""NoteRepository: round-trips, ordering, tags, folders (FR-1, FR-3, FR-7)."""

import pytest

from astranotes.domain.note import Note
from astranotes.errors import NoteNotFoundError


def test_save_and_get_roundtrip(repo):
    note = Note(title="Hello", content="body", tags=["work"])
    repo.save(note)
    loaded = repo.get(note.note_id)
    assert loaded is not None
    assert (loaded.title, loaded.content, loaded.tags) == ("Hello", "body", ["work"])


def test_get_missing_returns_none(repo):
    assert repo.get("nope") is None


def test_load_all_orders_by_last_modified_desc(repo):
    repo.save(Note(title="A"))
    repo.save(Note(title="B"))
    titles = [n.title for n in repo.load_all()]
    assert titles[0] == "B" and "A" in titles  # most recently saved first


def test_load_all_empty(repo):
    assert repo.load_all() == []


def test_delete_removes_note(repo):
    note = repo.save(Note(title="x"))
    repo.delete(note.note_id)
    assert repo.get(note.note_id) is None


def test_delete_missing_raises(repo):
    with pytest.raises(NoteNotFoundError):
        repo.delete("ghost")


def test_tags_roundtrip_and_filter(repo):
    repo.save(Note(title="tagged", tags=["alpha", "beta"]))
    repo.save(Note(title="other", tags=["beta"]))
    assert set(repo.list_tags()) == {"alpha", "beta"}
    assert {n.title for n in repo.load_all(tag="beta")} == {"tagged", "other"}
    assert {n.title for n in repo.load_all(tag="alpha")} == {"tagged"}


def test_folder_create_and_filter(repo):
    fid = repo.create_folder("Work")
    repo.save(Note(title="in-folder", folder_id=fid))
    repo.save(Note(title="loose"))
    assert {n.title for n in repo.load_all(folder_id=fid)} == {"in-folder"}


def test_duplicate_folder_rejected(repo):
    repo.create_folder("Work")
    with pytest.raises(ValueError):
        repo.create_folder("Work")


def test_empty_folder_name_rejected(repo):
    with pytest.raises(ValueError):
        repo.create_folder("   ")
