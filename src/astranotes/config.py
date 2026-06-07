"""Application configuration and key management.

Keys are read from the environment first and, in development only, generated
into the git-ignored `instance/` directory on first run. No key is ever
hardcoded in source (SEC). In the Week 4.2 deployment diagram the key lived in
an OS keychain node separate from the note data; the env / keyfile split here is
the local-first equivalent of that isolation.
"""

import hashlib
import os
import secrets
from dataclasses import dataclass
from pathlib import Path

from cryptography.fernet import Fernet

from astranotes.errors import ConfigError


@dataclass
class AppConfig:
    db_path: str
    encryption_key: bytes
    secret_key: str
    passphrase_sha256: str | None = None

    @property
    def requires_passphrase(self) -> bool:
        """Whether a passphrase gate is configured for unlocking SecureNotes."""
        return bool(self.passphrase_sha256)

    def check_passphrase(self, passphrase: str) -> bool:
        """True if the gate is open (no passphrase set) or the hash matches."""
        if not self.passphrase_sha256:
            return True
        digest = hashlib.sha256((passphrase or "").encode("utf-8")).hexdigest()
        return secrets.compare_digest(digest, self.passphrase_sha256)


def load_config(instance_dir: str | None = None) -> AppConfig:
    instance = Path(instance_dir or os.environ.get("ASTRANOTES_INSTANCE", "instance"))
    instance.mkdir(parents=True, exist_ok=True)

    db_path = os.environ.get("ASTRANOTES_DB_PATH") or str(instance / "astranotes.db")

    env_key = os.environ.get("ASTRANOTES_ENCRYPTION_KEY")
    if env_key:
        encryption_key = env_key.encode("utf-8")
    else:
        key_file = instance / "encryption.key"
        if key_file.exists():
            encryption_key = key_file.read_bytes()
        else:
            encryption_key = Fernet.generate_key()
            key_file.write_bytes(encryption_key)
            # Best-effort owner-only permissions. This dev fallback co-locates the
            # key with the database, which weakens at-rest protection — production
            # should supply ASTRANOTES_ENCRYPTION_KEY from a keychain/env instead.
            try:
                key_file.chmod(0o600)
            except OSError:
                pass

    secret_key = os.environ.get("ASTRANOTES_SECRET_KEY")
    if not secret_key:
        secret_file = instance / "flask_secret"
        if secret_file.exists():
            secret_key = secret_file.read_text(encoding="utf-8").strip()
        else:
            secret_key = secrets.token_hex(32)
            secret_file.write_text(secret_key, encoding="utf-8")

    passphrase_sha256 = os.environ.get("ASTRANOTES_PASSPHRASE_SHA256") or None

    # Fail fast with a clear message rather than surfacing a cryptic error deep in
    # request handling: the key must be a valid Fernet key and the database
    # directory must be creatable. The happy path is unchanged — an unset key is
    # generated above and validates trivially here.
    try:
        Fernet(encryption_key)
    except (ValueError, TypeError) as exc:
        raise ConfigError(
            "ASTRANOTES_ENCRYPTION_KEY is not a valid Fernet key (expected a "
            "url-safe base64-encoded 32-byte key). Generate one with: "
            'python -c "from cryptography.fernet import Fernet; '
            'print(Fernet.generate_key().decode())"'
        ) from exc

    db_parent = Path(db_path).expanduser().parent
    try:
        db_parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ConfigError(f"Cannot create the database directory {db_parent}: {exc}") from exc

    return AppConfig(
        db_path=db_path,
        encryption_key=encryption_key,
        secret_key=secret_key,
        passphrase_sha256=passphrase_sha256,
    )
