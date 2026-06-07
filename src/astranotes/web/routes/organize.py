"""Folders, tags, and full-text search (FR-4, FR-7)."""

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from astranotes.errors import NoteNotFoundError
from astranotes.web.deps import get_service

bp = Blueprint("organize", __name__)


@bp.post("/folders")
def create_folder():
    svc = get_service()
    name = request.form.get("name", "")
    try:
        svc.create_folder(name)
        flash(f"Folder {name.strip()!r} created.", "success")
    except ValueError as exc:
        flash(str(exc), "warning")
    return redirect(request.referrer or url_for("pages.index"))


@bp.post("/notes/<note_id>/move")
def move(note_id):
    svc = get_service()
    try:
        svc.move_note(note_id, request.form.get("folder_id") or None)
    except NoteNotFoundError:
        abort(404)
    flash("Note moved.", "success")
    return redirect(url_for("notes.view", note_id=note_id))


@bp.get("/search")
def search():
    svc = get_service()
    query = request.args.get("q", "")
    results = svc.search_notes(query) if query.strip() else []
    return render_template("search.html", query=query, results=results)
