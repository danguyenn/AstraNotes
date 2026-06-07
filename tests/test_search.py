"""Full-text search, including the Week 3.1 edge cases (FR-4)."""


def test_search_hit(service):
    service.create_note("Project Kickoff", "agenda and notes")
    results = service.search_notes("kickoff")
    assert len(results) == 1
    assert results[0]["note"].title == "Project Kickoff"


def test_empty_query_returns_nothing(service):
    service.create_note("anything", "body")
    assert service.search_notes("") == []
    assert service.search_notes("   ") == []


def test_no_results(service):
    service.create_note("anything", "body")
    assert service.search_notes("zzzznomatch") == []


def test_special_characters_do_not_crash(service):
    service.create_note("Q3 Budget", "money & forecast")
    # An apostrophe / ampersand would break a raw FTS query; it must be tokenized.
    assert service.search_notes("budget & forecast'") != []


def test_locked_note_excluded_from_search(service):
    note = service.create_note("Secret Plan", "classified content here")
    service.make_private(note.note_id)
    assert service.search_notes("classified") == []
    assert service.search_notes("Secret") == []


def test_search_reflects_edits(service):
    note = service.create_note("Title", "original")
    service.edit_note(note.note_id, "Title", "replaced keyword zebra")
    assert service.search_notes("zebra") != []
    assert service.search_notes("original") == []
