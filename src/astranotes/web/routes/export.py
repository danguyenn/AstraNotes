"""Export notes as Markdown — single file or a folder as a .zip (FR-8).

Filenames are derived from note titles and sanitized so a title like
"Q3 / Budget & Forecast" cannot produce an invalid path on Windows. Locked
notes are skipped in a bulk export rather than leaking ciphertext into the zip.
"""

import io
import re
import zipfile

from flask import Blueprint, Response, abort, flash, redirect, request, url_for

from astranotes.web.deps import get_service, get_session

bp = Blueprint("export", __name__)

_INVALID = re.compile(r'[\\/:*?"<>|]+')


def _safe_filename(title: str) -> str:
    name = _INVALID.sub("_", title).strip().strip(".") or "note"
    return name[:80] + ".md"


def _as_markdown(title: str, content: str) -> str:
    return f"# {title}\n\n{content}\n"


@bp.get("/notes/<note_id>/export")
def export_one(note_id):
    svc, session = get_service(), get_session()
    note = svc.get_note(note_id)
    if note is None:
        abort(404)
    content = svc.reveal(note, session)
    if content is None:
        flash("Unlock this note before exporting it.", "warning")
        return redirect(
            url_for("secure.unlock_prompt", next=url_for("notes.view", note_id=note_id))
        )
    return Response(
        _as_markdown(note.title, content),
        mimetype="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{_safe_filename(note.title)}"'},
    )


@bp.get("/export")
def export_bulk():
    svc, session = get_service(), get_session()
    folder_id = request.args.get("folder") or None
    buffer = io.BytesIO()
    used: dict[str, int] = {}
    count = 0
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for note in svc.list_notes(folder_id=folder_id):
            content = svc.reveal(note, session)
            if content is None:
                continue  # skip locked notes in bulk export
            name = _unique(_safe_filename(note.title), used)
            archive.writestr(name, _as_markdown(note.title, content))
            count += 1
    if count == 0:
        flash("This selection has no exportable notes.", "warning")
        return redirect(request.referrer or url_for("pages.index"))
    buffer.seek(0)
    return Response(
        buffer.read(),
        mimetype="application/zip",
        headers={"Content-Disposition": 'attachment; filename="astranotes-export.zip"'},
    )


def _unique(name: str, used: dict[str, int]) -> str:
    if name not in used:
        used[name] = 1
        return name
    used[name] += 1
    stem = name.removesuffix(".md")
    return f"{stem}-{used[name]}.md"
