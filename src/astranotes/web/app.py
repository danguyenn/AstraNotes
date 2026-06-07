"""Flask application factory.

Wires the layers together (config → storage → repository → encryption →
service), registers the route blueprints, the Markdown filter, the sidebar
context, and the error handler. Tests build an app the same way by passing a
config that points at a temporary database.
"""

import logging
import os

from flask import Flask, render_template

from astranotes.config import AppConfig, load_config
from astranotes.services.encryption_service import EncryptionService
from astranotes.services.note_service import NoteService
from astranotes.storage.local_storage import LocalStorage
from astranotes.storage.note_repository import NoteRepository
from astranotes.web import deps
from astranotes.web.markdown_render import render_markdown
from astranotes.web.routes import register_routes

logger = logging.getLogger("astranotes")


def create_app(config: AppConfig | None = None) -> Flask:
    app = Flask(__name__)
    cfg = config or load_config()

    # Configure logging once (idempotent — a no-op if the root logger already has
    # handlers, e.g. under pytest or a WSGI server). Level is overridable via env.
    logging.basicConfig(
        level=os.environ.get("ASTRANOTES_LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    # Non-secret startup line only: a filesystem path and a boolean. Never the key,
    # secret_key, passphrase hash, or any note content.
    logger.info(
        "AstraNotes starting (db=%s, passphrase_gate=%s)", cfg.db_path, cfg.requires_passphrase
    )

    storage = LocalStorage(cfg.db_path)
    repository = NoteRepository(storage)
    encryption = EncryptionService(cfg.encryption_key)
    service = NoteService(repository, encryption)

    app.secret_key = cfg.secret_key
    app.config["ASTRANOTES_CONFIG"] = cfg
    app.config["ASTRANOTES_SERVICE"] = service
    app.jinja_env.filters["markdown"] = render_markdown

    register_routes(app)

    @app.after_request
    def set_security_headers(response):
        # Defensive headers. setdefault() so a route that sets its own header (e.g.
        # the export Content-Type asserted by tests) is never overridden. Scripts and
        # styles are same-origin (no CDN — NFR-1); 'unsafe-inline' on script-src is
        # required only because view.html uses an inline onsubmit confirm() on delete.
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'",
        )
        return response

    @app.context_processor
    def inject_sidebar():
        return {
            "sidebar_folders": service.list_folders(),
            "sidebar_tags": service.list_tags(),
            "session_unlocked": deps.get_session().is_unlocked,
            "requires_passphrase": cfg.requires_passphrase,
        }

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", code=404, message="That page could not be found."), 404

    return app


def main() -> None:
    """Console-script entry point: development server on 127.0.0.1:5000.

    Debug (the Werkzeug interactive debugger) is off unless ASTRANOTES_DEBUG=1,
    so an exception page can't expose a code console by default.
    """
    debug = os.environ.get("ASTRANOTES_DEBUG") == "1"
    create_app().run(host="127.0.0.1", port=5000, debug=debug)


if __name__ == "__main__":
    main()
