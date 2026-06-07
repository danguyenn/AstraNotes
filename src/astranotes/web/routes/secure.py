"""SecureNote privacy and the session unlock gate (FR-5).

`lock` / `make-public` change a note's at-rest state (encrypt / decrypt).
`unlock` / `lock-session` change whether locked notes are revealed for the
current browser session. Revealing plaintext — viewing, editing, or making a
note public again — always requires an unlocked session, mediated by the
optional passphrase gate.
"""

import logging

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask import session as flask_session

from astranotes.errors import EncryptionError, NoteNotFoundError
from astranotes.web.deps import get_config, get_service, get_session

bp = Blueprint("secure", __name__)
logger = logging.getLogger("astranotes.secure")


def _safe_next(target: str | None, fallback: str) -> str:
    """Only allow same-origin relative redirect targets (no open redirect)."""
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return fallback


@bp.post("/notes/<note_id>/lock")
def lock(note_id):
    svc = get_service()
    try:
        svc.make_private(note_id)
        logger.info("note locked note_id=%s", note_id)
        flash("Note locked — its body is now encrypted at rest.", "success")
    except NoteNotFoundError:
        abort(404)
    except EncryptionError:
        logger.warning("encryption failed locking note_id=%s", note_id)
        flash("Could not encrypt the note.", "danger")
    return redirect(url_for("notes.view", note_id=note_id))


@bp.post("/notes/<note_id>/make-public")
def make_public(note_id):
    svc, session = get_service(), get_session()
    # Making a note public decrypts its body, so it needs an unlocked session —
    # the same gate that viewing and editing a locked note use (consistent with
    # NoteService.reveal).
    if not session.is_unlocked:
        return redirect(
            url_for("secure.unlock_prompt", next=url_for("notes.view", note_id=note_id))
        )
    try:
        svc.make_public(note_id)
        logger.info("note made public note_id=%s", note_id)
        flash("Note unlocked — its body is stored as plain text again.", "success")
    except NoteNotFoundError:
        abort(404)
    except EncryptionError:
        logger.warning("decryption failed making public note_id=%s", note_id)
        flash("Could not decrypt the note.", "danger")
    return redirect(url_for("notes.view", note_id=note_id))


@bp.get("/unlock")
def unlock_prompt():
    nxt = _safe_next(request.args.get("next"), url_for("pages.index"))
    return render_template("unlock.html", next=nxt)


@bp.post("/unlock")
def unlock():
    cfg = get_config()
    nxt = _safe_next(request.form.get("next"), url_for("pages.index"))
    if cfg.check_passphrase(request.form.get("passphrase", "")):
        flask_session["unlocked"] = True
        logger.info("secure session unlocked")
        flash("Secure notes unlocked for this session.", "success")
        return redirect(nxt)
    logger.warning("secure session unlock rejected (incorrect passphrase)")
    flash("Incorrect passphrase.", "warning")
    return redirect(url_for("secure.unlock_prompt", next=nxt))


@bp.post("/lock-session")
def lock_session():
    flask_session["unlocked"] = False
    logger.info("secure session locked")
    flash("Secure notes locked.", "success")
    return redirect(url_for("pages.index"))
