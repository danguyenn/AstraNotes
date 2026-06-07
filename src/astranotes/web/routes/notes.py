"""Note CRUD, version history, and restore (FR-1, FR-2, FR-3, FR-6).

Routes here carry no business logic. The one thing they own is the NFR-2 split:
a ValueError (bad input) flashes a warning and re-renders the form, while a
StorageError (write failure) flashes a danger message — two visually distinct
error paths so the user can tell what kind of failure occurred.
"""

import logging

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from astranotes.errors import NoteNotFoundError, StorageError
from astranotes.web.deps import get_service, get_session

bp = Blueprint("notes", __name__)
logger = logging.getLogger("astranotes.notes")


def _parse_tags(raw: str) -> list[str]:
    seen, out = set(), []
    for part in (raw or "").split(","):
        name = part.strip()
        if name and name.lower() not in seen:
            seen.add(name.lower())
            out.append(name)
    return out


@bp.get("/notes/new")
def new():
    svc = get_service()
    return render_template("editor.html", note=None, content="", folders=svc.list_folders())


@bp.post("/notes")
def create():
    svc = get_service()
    title = request.form.get("title", "")
    content = request.form.get("content", "")
    folder_id = request.form.get("folder_id") or None
    tags = _parse_tags(request.form.get("tags", ""))
    try:
        note = svc.create_note(title, content, folder_id=folder_id, tags=tags)
    except ValueError as exc:
        flash(str(exc), "warning")
        return render_template(
            "editor.html", note=None, content=content, folders=svc.list_folders()
        ), 400
    except StorageError:
        logger.error("storage error creating note", exc_info=True)
        flash("Could not save the note due to a storage error.", "danger")
        return render_template(
            "editor.html", note=None, content=content, folders=svc.list_folders()
        ), 500
    flash("Note created.", "success")
    return redirect(url_for("notes.view", note_id=note.note_id))


@bp.get("/notes/<note_id>")
def view(note_id):
    svc, session = get_service(), get_session()
    note = svc.get_note(note_id)
    if note is None:
        abort(404)
    if note.is_locked and not session.is_unlocked:
        flash("This note is locked. Unlock it to view the contents.", "warning")
        return redirect(
            url_for("secure.unlock_prompt", next=url_for("notes.view", note_id=note_id))
        )
    return render_template("view.html", note=note, content=svc.reveal(note, session))


@bp.get("/notes/<note_id>/edit")
def edit_form(note_id):
    svc, session = get_service(), get_session()
    note = svc.get_note(note_id)
    if note is None:
        abort(404)
    if note.is_locked and not session.is_unlocked:
        flash("Unlock this note to edit it.", "warning")
        return redirect(
            url_for("secure.unlock_prompt", next=url_for("notes.edit_form", note_id=note_id))
        )
    return render_template(
        "editor.html",
        note=note,
        content=svc.reveal(note, session) or "",
        folders=svc.list_folders(),
    )


@bp.post("/notes/<note_id>")
def update(note_id):
    svc = get_service()
    note = svc.get_note(note_id)
    if note is None:
        abort(404)
    title = request.form.get("title", "")
    content = request.form.get("content", "")
    folder_id = request.form.get("folder_id") or None
    tags = _parse_tags(request.form.get("tags", ""))
    try:
        svc.edit_note(note_id, title, content, folder_id=folder_id, tags=tags)
    except ValueError as exc:
        flash(str(exc), "warning")
        return render_template(
            "editor.html", note=note, content=content, folders=svc.list_folders()
        ), 400
    except StorageError:
        logger.error("storage error updating note_id=%s", note_id, exc_info=True)
        flash("Could not save changes due to a storage error.", "danger")
        return render_template(
            "editor.html", note=note, content=content, folders=svc.list_folders()
        ), 500
    flash("Note saved.", "success")
    return redirect(url_for("notes.view", note_id=note_id))


@bp.post("/notes/<note_id>/delete")
def delete(note_id):
    svc = get_service()
    try:
        svc.delete_note(note_id)
    except NoteNotFoundError:
        abort(404)
    except StorageError:
        logger.error("storage error deleting note_id=%s", note_id, exc_info=True)
        flash("Could not delete the note due to a storage error.", "danger")
        return redirect(url_for("notes.view", note_id=note_id))
    flash("Note deleted. Its version history is retained for recovery.", "success")
    return redirect(url_for("pages.index"))


@bp.get("/notes/<note_id>/history")
def history(note_id):
    svc, session = get_service(), get_session()
    note = svc.get_note(note_id)
    if note is None:
        abort(404)
    # Enforce the lock gate in the route, not just the template — consistent with
    # view/edit_form, so version snapshots of a locked note stay protected.
    if note.is_locked and not session.is_unlocked:
        flash("Unlock this note to view its history.", "warning")
        return redirect(
            url_for("secure.unlock_prompt", next=url_for("notes.history", note_id=note_id))
        )
    return render_template("history.html", note=note, versions=svc.list_versions(note_id))


@bp.post("/notes/<note_id>/restore/<version_id>")
def restore(note_id, version_id):
    svc = get_service()
    try:
        svc.restore_version(note_id, version_id)
    except NoteNotFoundError:
        abort(404)
    logger.info("version restored note_id=%s version_id=%s", note_id, version_id)
    flash("Version restored. The restore is itself reversible.", "success")
    return redirect(url_for("notes.view", note_id=note_id))
