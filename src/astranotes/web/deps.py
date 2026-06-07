"""Request-scoped dependency accessors.

Routes pull their collaborators through these helpers instead of importing the
storage layer directly, which keeps the import direction honest: web depends on
services, never on storage.
"""

from flask import current_app, g
from flask import session as flask_session

from astranotes.services.session import UserSession


def get_config():
    return current_app.config["ASTRANOTES_CONFIG"]


def get_service():
    return current_app.config["ASTRANOTES_SERVICE"]


def get_session() -> UserSession:
    """Map the Flask cookie's unlock flag onto a domain UserSession, once per
    request."""
    if "user_session" not in g:
        g.user_session = UserSession(unlocked=bool(flask_session.get("unlocked", False)))
    return g.user_session
