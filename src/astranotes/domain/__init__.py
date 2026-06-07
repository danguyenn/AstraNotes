"""Domain layer: pure entities and invariants with no outward dependencies."""

from astranotes.domain.note import Note, SecureNote

__all__ = ["Note", "SecureNote"]
