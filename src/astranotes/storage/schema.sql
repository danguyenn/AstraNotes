-- AstraNotes local SQLite schema.
--
-- The user_id columns are placeholders: single-user local-first is the current
-- scope, but leaving the column in means multi-user accounts (the deferred
-- Supabase-era requirement) can be added later without restructuring tables.

CREATE TABLE IF NOT EXISTS folders (
    folder_id   TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    user_id     TEXT,
    UNIQUE (name, user_id)
);

CREATE TABLE IF NOT EXISTS notes (
    note_id            TEXT PRIMARY KEY,
    title              TEXT NOT NULL,
    content            TEXT NOT NULL DEFAULT '',
    folder_id          TEXT,
    is_locked          INTEGER NOT NULL DEFAULT 0,
    encryption_key_ref TEXT,
    user_id            TEXT,
    created_at         TEXT NOT NULL,
    last_modified      TEXT NOT NULL,
    FOREIGN KEY (folder_id) REFERENCES folders (folder_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tags (
    tag_id  TEXT PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS note_tags (
    note_id TEXT NOT NULL,
    tag_id  TEXT NOT NULL,
    PRIMARY KEY (note_id, tag_id)
);

-- Version snapshots deliberately have NO foreign key to notes: they must
-- survive note deletion so a deleted note can still be restored (FR-3 + FR-6).
-- Keep the implicit rowid (do NOT add WITHOUT ROWID): VersionHistory.list_for
-- relies on `ORDER BY rowid DESC` for stable newest-first ordering, since two
-- snapshots can share an identical created_at timestamp.
CREATE TABLE IF NOT EXISTS note_versions (
    version_id       TEXT PRIMARY KEY,
    note_id          TEXT NOT NULL,
    title_snapshot   TEXT NOT NULL,
    content_snapshot TEXT NOT NULL,
    created_at       TEXT NOT NULL
);

-- Full-text search over title + body (FR-4). Locked notes are kept out of this
-- index so their content cannot be discovered while encrypted.
CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5 (
    note_id UNINDEXED,
    title,
    content
);

-- Append-only audit log for security-sensitive events (lock / unlock /
-- restore). The triggers below reject UPDATE and DELETE at the database level,
-- so the trail is tamper-evident — the local-first echo of the original
-- SPR-03 / SEC requirement.
CREATE TABLE IF NOT EXISTS audit_log (
    event_id        TEXT PRIMARY KEY,
    action          TEXT NOT NULL,
    target_note_id  TEXT,
    created_at      TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS audit_log_no_update
BEFORE UPDATE ON audit_log
BEGIN
    SELECT RAISE(ABORT, 'audit_log is append-only');
END;

CREATE TRIGGER IF NOT EXISTS audit_log_no_delete
BEFORE DELETE ON audit_log
BEGIN
    SELECT RAISE(ABORT, 'audit_log is append-only');
END;
