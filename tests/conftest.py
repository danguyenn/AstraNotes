"""Shared fixtures.

Every fixture is isolated per test via `tmp_path`, so the SQLite file is
throwaway and tests never leak state into one another (NFR-3).
"""

import pytest
from cryptography.fernet import Fernet

from astranotes.config import AppConfig
from astranotes.services.encryption_service import EncryptionService
from astranotes.services.note_service import NoteService
from astranotes.storage.local_storage import LocalStorage
from astranotes.storage.note_repository import NoteRepository
from astranotes.web.app import create_app


@pytest.fixture
def storage(tmp_path):
    return LocalStorage(tmp_path / "test.db")


@pytest.fixture
def repo(storage):
    return NoteRepository(storage)


@pytest.fixture
def enc():
    return EncryptionService(Fernet.generate_key())


@pytest.fixture
def service(repo, enc):
    return NoteService(repo, enc)


@pytest.fixture
def app(tmp_path):
    cfg = AppConfig(
        db_path=str(tmp_path / "web.db"),
        encryption_key=Fernet.generate_key(),
        secret_key="test-secret",
        passphrase_sha256=None,
    )
    return create_app(cfg)


@pytest.fixture
def client(app):
    return app.test_client()
