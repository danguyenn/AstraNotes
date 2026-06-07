"""Version history and restore, including retention on delete (FR-6, FR-3)."""


def test_save_creates_a_version(service):
    note = service.create_note("Title", "v1")
    assert len(service.list_versions(note.note_id)) == 1


def test_each_save_adds_a_version(service):
    note = service.create_note("Title", "v1")
    service.edit_note(note.note_id, "Title", "v2")
    service.edit_note(note.note_id, "Title", "v3")
    assert len(service.list_versions(note.note_id)) == 3


def test_restore_reverts_content(service):
    note = service.create_note("Title", "original")
    service.edit_note(note.note_id, "Title", "changed")
    versions = service.list_versions(note.note_id)
    oldest = versions[-1]
    service.restore_version(note.note_id, oldest["version_id"])
    assert service.get_note(note.note_id).content == "original"


def test_restore_is_itself_reversible(service):
    note = service.create_note("Title", "original")
    service.edit_note(note.note_id, "Title", "changed")
    count_before = len(service.list_versions(note.note_id))
    oldest = service.list_versions(note.note_id)[-1]
    service.restore_version(note.note_id, oldest["version_id"])
    assert len(service.list_versions(note.note_id)) == count_before + 1


def test_versions_retained_after_delete(service):
    note = service.create_note("Title", "v1")
    service.edit_note(note.note_id, "Title", "v2")
    service.delete_note(note.note_id)
    assert service.get_note(note.note_id) is None
    assert len(service.list_versions(note.note_id)) == 2
