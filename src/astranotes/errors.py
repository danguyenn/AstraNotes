"""Domain-level error types.

These let upper layers handle failures without importing the database driver or
the encryption library, which keeps the layer boundaries honest (NFR-3) and
gives the web layer distinct, user-facing error paths (NFR-2).
"""


class AstraNotesError(Exception):
    """Base class for every AstraNotes domain error."""


class StorageError(AstraNotesError):
    """A persistence operation failed. Wraps the underlying sqlite3 error so no
    caller above the storage layer depends on the database driver."""


class EncryptionError(AstraNotesError):
    """Encrypting or decrypting a SecureNote failed — a missing/invalid key or
    tampered ciphertext (FR-5)."""


class NoteNotFoundError(AstraNotesError):
    """An operation targeted a note id that does not exist."""


class ConfigError(AstraNotesError):
    """Application configuration is invalid or the environment is unusable — an
    ill-formed encryption key or an uncreatable database directory. Raised at
    startup so misconfiguration fails fast with a clear message (NFR-2)."""
