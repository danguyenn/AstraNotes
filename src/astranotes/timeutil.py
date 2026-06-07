"""ISO-8601 UTC timestamp helpers shared by every layer.

Timestamps are stored as ISO strings in SQLite and parsed back into aware
datetimes by the repository, so the rest of the system works with real datetime
objects rather than strings.
"""

from datetime import UTC, datetime


def utcnow() -> datetime:
    """Timezone-aware current time in UTC."""
    return datetime.now(UTC)


def now_iso() -> str:
    """Current UTC time as an ISO-8601 string."""
    return utcnow().isoformat()
