"""EncryptionService: symmetric encryption for SecureNote bodies (FR-5).

Wraps Fernet (AES-128-CBC + HMAC). The service is handed a key; it never reads
the key store itself. That separation mirrors the Week 4.2 deployment design,
where the key lived in an OS keychain node isolated from the note data.
"""

from cryptography.fernet import Fernet, InvalidToken

from astranotes.errors import EncryptionError


class EncryptionService:
    def __init__(self, key: bytes) -> None:
        try:
            self._fernet = Fernet(key)
        except (ValueError, TypeError) as exc:
            raise EncryptionError("Invalid encryption key.") from exc

    def encrypt(self, plaintext: str) -> str:
        """Return a base64 token (stored as the note's content at rest)."""
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, token: str) -> str:
        """Recover plaintext, raising EncryptionError on a bad/tampered token."""
        try:
            return self._fernet.decrypt(token.encode("utf-8")).decode("utf-8")
        except (InvalidToken, ValueError) as exc:
            raise EncryptionError("Could not decrypt note content.") from exc
