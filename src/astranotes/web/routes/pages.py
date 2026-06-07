"""Top-level pages: the notes dashboard, profile, and settings."""

from flask import Blueprint, render_template, request

from astranotes.web.deps import get_service, get_session

bp = Blueprint("pages", __name__)


@bp.get("/")
def index():
    svc = get_service()
    session = get_session()
    folder_id = request.args.get("folder") or None
    tag = request.args.get("tag") or None
    notes = svc.list_notes(folder_id=folder_id, tag=tag)
    items = [{"note": note, "preview": svc.reveal(note, session)} for note in notes]
    return render_template("index.html", items=items, active_folder=folder_id, active_tag=tag)


@bp.get("/profile")
def profile():
    return render_template("profile.html")


@bp.get("/settings")
def settings():
    svc = get_service()
    return render_template("settings.html", events=svc.audit_events())
