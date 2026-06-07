"""UserSession: in-memory unlock state for SecureNotes (FR-5).

The Flask cookie maps onto this domain object so the domain and service layers
never import Flask. While locked, encrypted notes are shown as placeholders and
their content stays out of reach; unlocking reveals them for the session.
"""


class UserSession:
    def __init__(self, unlocked: bool = False) -> None:
        self._unlocked = unlocked

    @property
    def is_unlocked(self) -> bool:
        return self._unlocked

    def unlock(self) -> None:
        self._unlocked = True

    def lock(self) -> None:
        self._unlocked = False
