"""Note and SecureNote domain entities.

The title invariant lives in the constructor rather than in NoteService. This is
a deliberate decision carried over from the Week 6 realization: if validation
sat in the service, another caller could construct an invalid Note directly. In
the constructor, an invalid Note cannot exist in the system at all.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from astranotes.timeutil import utcnow

# Marker stored in encryption_key_ref so a locked note records which key store
# encrypted it. A single local key is used today; the reference leaves room for
# rotation later without a schema change.
DEFAULT_KEY_REF = "local-fernet-v1"


def _validate(title: str, content: str) -> str:
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Note title must be a non-empty string.")
    if not isinstance(content, str):
        raise ValueError("Note content must be a string.")
    return title.strip()


@dataclass
class Note:
    """A Markdown note (FR-1). `content` holds Markdown source; for a locked
    note it holds ciphertext at rest (FR-5)."""

    title: str
    content: str = ""
    note_id: str = field(default_factory=lambda: str(uuid4()))
    folder_id: str | None = None
    tags: list[str] = field(default_factory=list)
    is_locked: bool = False
    encryption_key_ref: str | None = None
    created_at: datetime = field(default_factory=utcnow)
    last_modified: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        self.title = _validate(self.title, self.content)

    def update_content(self, title: str, content: str) -> None:
        """Apply an edit (FR-2), re-checking the same invariant and bumping the
        modified timestamp."""
        self.title = _validate(title, content)
        self.content = content
        self.last_modified = utcnow()


@dataclass
class SecureNote(Note):
    """A note marked private. Its body is encrypted at rest and it is excluded
    from search while locked (FR-5)."""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.is_locked = True
        if self.encryption_key_ref is None:
            self.encryption_key_ref = DEFAULT_KEY_REF

    def lock(self) -> None:
        self.is_locked = True

    def unlock(self) -> None:
        self.is_locked = False
