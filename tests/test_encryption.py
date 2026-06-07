"""EncryptionService round-trips and failure handling (FR-5)."""

import pytest
from cryptography.fernet import Fernet

from astranotes.errors import EncryptionError
from astranotes.services.encryption_service import EncryptionService


def test_encrypt_decrypt_roundtrip(enc):
    token = enc.encrypt("secret body")
    assert enc.decrypt(token) == "secret body"


def test_ciphertext_differs_from_plaintext(enc):
    token = enc.encrypt("secret body")
    assert "secret body" not in token


def test_decrypt_bad_token_raises(enc):
    with pytest.raises(EncryptionError):
        enc.decrypt("not-a-valid-token")


def test_wrong_key_cannot_decrypt():
    a = EncryptionService(Fernet.generate_key())
    b = EncryptionService(Fernet.generate_key())
    with pytest.raises(EncryptionError):
        b.decrypt(a.encrypt("hello"))


def test_invalid_key_raises():
    with pytest.raises(EncryptionError):
        EncryptionService(b"not-a-fernet-key")
