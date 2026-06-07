"""Configuration loading and fail-fast validation (NFR-2).

These exercise `load_config` directly, including the branches that reject an
ill-formed encryption key or an uncreatable database directory at startup.
"""

import pytest
from cryptography.fernet import Fernet

from astranotes.config import AppConfig, load_config
from astranotes.errors import ConfigError

_ENV_VARS = (
    "ASTRANOTES_ENCRYPTION_KEY",
    "ASTRANOTES_SECRET_KEY",
    "ASTRANOTES_DB_PATH",
    "ASTRANOTES_PASSPHRASE_SHA256",
    "ASTRANOTES_INSTANCE",
)


@pytest.fixture
def clean_env(monkeypatch):
    """Isolate from any ASTRANOTES_* vars in the ambient environment."""
    for name in _ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def test_generates_valid_key_when_unset(clean_env, tmp_path):
    cfg = load_config(instance_dir=str(tmp_path))
    assert isinstance(cfg, AppConfig)
    Fernet(cfg.encryption_key)  # a generated key must be usable
    assert cfg.requires_passphrase is False


def test_uses_env_key(clean_env, tmp_path):
    key = Fernet.generate_key().decode()
    clean_env.setenv("ASTRANOTES_ENCRYPTION_KEY", key)
    cfg = load_config(instance_dir=str(tmp_path))
    assert cfg.encryption_key == key.encode()


def test_invalid_encryption_key_raises_config_error(clean_env, tmp_path):
    clean_env.setenv("ASTRANOTES_ENCRYPTION_KEY", "not-a-valid-fernet-key")
    with pytest.raises(ConfigError, match="ASTRANOTES_ENCRYPTION_KEY"):
        load_config(instance_dir=str(tmp_path))


def test_uncreatable_db_dir_raises_config_error(clean_env, tmp_path):
    # An ancestor of the db path is a regular file, so the parent dir can't be made.
    blocker = tmp_path / "afile"
    blocker.write_text("x", encoding="utf-8")
    clean_env.setenv("ASTRANOTES_DB_PATH", str(blocker / "sub" / "astranotes.db"))
    with pytest.raises(ConfigError, match="database directory"):
        load_config(instance_dir=str(tmp_path))
