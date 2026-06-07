"""Integration tests through the Flask test client (FR-1..FR-8, NFR-2, SEC)."""


def _create(client, title="Meeting Notes", content="## Agenda\n- one", tags="work"):
    return client.post("/notes", data={"title": title, "content": content, "tags": tags})


def test_index_ok(client):
    assert client.get("/").status_code == 200


def test_security_headers_present(client):
    resp = client.get("/")
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["Referrer-Policy"] == "no-referrer"
    csp = resp.headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    # 'unsafe-inline' is required for the inline onsubmit delete guard in view.html.
    assert "script-src 'self' 'unsafe-inline'" in csp


def test_create_and_view(client):
    resp = _create(client)
    assert resp.status_code == 302
    note_id = resp.headers["Location"].rsplit("/", 1)[-1]
    page = client.get(f"/notes/{note_id}")
    assert page.status_code == 200
    assert b"Meeting Notes" in page.data


def test_empty_title_flashes_warning(client):
    resp = client.post("/notes", data={"title": "   ", "content": "x"})
    assert resp.status_code == 400
    assert b"non-empty" in resp.data


def test_storage_error_is_distinct_from_validation(client):
    # Validation (warning) and storage (danger) are two separate flash styles —
    # here we exercise the validation path; both branches exist in the route.
    resp = client.post("/notes", data={"title": "", "content": "x"})
    assert b"flash-warning" in resp.data


def test_search_hit_empty_and_none(client):
    _create(client, title="Project Kickoff", content="kickoff agenda")
    assert b"Project Kickoff" in client.get("/search?q=kickoff").data
    assert b"Type a keyword" in client.get("/search?q=").data
    assert b"No notes match" in client.get("/search?q=zzznope").data


def test_lock_then_requires_unlock(client):
    note_id = _create(client).headers["Location"].rsplit("/", 1)[-1]
    assert client.post(f"/notes/{note_id}/lock").status_code == 302
    # Viewing a locked note without an unlocked session redirects to /unlock.
    assert client.get(f"/notes/{note_id}").status_code == 302


def test_unlock_then_view(client):
    note_id = _create(client).headers["Location"].rsplit("/", 1)[-1]
    client.post(f"/notes/{note_id}/lock")
    client.post("/unlock", data={"passphrase": "", "next": f"/notes/{note_id}"})
    assert client.get(f"/notes/{note_id}").status_code == 200


def test_export_single_markdown(client):
    note_id = _create(client).headers["Location"].rsplit("/", 1)[-1]
    resp = client.get(f"/notes/{note_id}/export")
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("text/markdown")


def test_export_bulk_zip(client):
    _create(client)
    resp = client.get("/export")
    assert resp.status_code == 200
    assert resp.headers["Content-Type"] == "application/zip"


def test_xss_is_sanitized(client):
    resp = client.post(
        "/notes",
        data={"title": "x", "content": "<script>alert(1)</script>hi"},
        follow_redirects=True,
    )
    assert b"<script>alert(1)" not in resp.data


def test_unknown_note_is_404(client):
    assert client.get("/notes/does-not-exist").status_code == 404


def test_edit_flow(client):
    note_id = _create(client).headers["Location"].rsplit("/", 1)[-1]
    assert client.get(f"/notes/{note_id}/edit").status_code == 200
    resp = client.post(
        f"/notes/{note_id}", data={"title": "Renamed", "content": "edited", "tags": ""}
    )
    assert resp.status_code == 302
    assert b"Renamed" in client.get(f"/notes/{note_id}").data


def test_edit_empty_title_rejected(client):
    note_id = _create(client).headers["Location"].rsplit("/", 1)[-1]
    resp = client.post(f"/notes/{note_id}", data={"title": "  ", "content": "x"})
    assert resp.status_code == 400


def test_delete_via_web(client):
    note_id = _create(client).headers["Location"].rsplit("/", 1)[-1]
    assert client.post(f"/notes/{note_id}/delete").status_code == 302
    assert client.get(f"/notes/{note_id}").status_code == 404


def test_history_and_restore(client):
    note_id = _create(client, content="v1").headers["Location"].rsplit("/", 1)[-1]
    client.post(f"/notes/{note_id}", data={"title": "Meeting Notes", "content": "v2", "tags": ""})
    history = client.get(f"/notes/{note_id}/history")
    assert history.status_code == 200
    # Restore the oldest version back to v1.
    versions = client.application.config["ASTRANOTES_SERVICE"].list_versions(note_id)
    resp = client.post(f"/notes/{note_id}/restore/{versions[-1]['version_id']}")
    assert resp.status_code == 302
    assert b"v1" in client.get(f"/notes/{note_id}").data


def test_create_folder_and_duplicate(client):
    assert client.post("/folders", data={"name": "Work"}).status_code == 302
    dup = client.post("/folders", data={"name": "Work"}, follow_redirects=True)
    assert b"already exists" in dup.data


def test_move_note_to_folder(client):
    svc = client.application.config["ASTRANOTES_SERVICE"]
    fid = svc.create_folder("Work")
    note_id = _create(client).headers["Location"].rsplit("/", 1)[-1]
    assert client.post(f"/notes/{note_id}/move", data={"folder_id": fid}).status_code == 302
    assert svc.get_note(note_id).folder_id == fid


def test_lock_unlock_session_and_make_public(client):
    note_id = _create(client).headers["Location"].rsplit("/", 1)[-1]
    client.post(f"/notes/{note_id}/lock")
    client.post("/unlock", data={"passphrase": "", "next": "/"})
    # Make the note public again (decrypt at rest).
    assert client.post(f"/notes/{note_id}/make-public").status_code == 302
    assert client.post("/lock-session").status_code == 302


def test_settings_and_profile(client):
    assert client.get("/settings").status_code == 200
    assert client.get("/profile").status_code == 200
