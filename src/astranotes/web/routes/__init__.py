"""Blueprint registration — the single place routes are wired into the app."""

from astranotes.web.routes import export, notes, organize, pages, secure


def register_routes(app) -> None:
    app.register_blueprint(pages.bp)
    app.register_blueprint(notes.bp)
    app.register_blueprint(organize.bp)
    app.register_blueprint(secure.bp)
    app.register_blueprint(export.bp)
