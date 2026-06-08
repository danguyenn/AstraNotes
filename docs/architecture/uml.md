# UML Design Package (Mermaid)

Reproduced from the Week 4.2 UML package and updated to the local-first
realization. The Week 5.2 traceability matrix flagged three behavioral gaps —
**no edit, delete, or search activity diagram** — and a weak failure-handling
story (NFR-2). Those gaps are **resolved here**: edit, delete, and search each
have an activity diagram, and the failure branches (storage write/read failure)
are modeled, not just input validation.

## 1. Class diagram

```mermaid
classDiagram
    class Note {
        +str note_id
        +str title
        +str content
        +str folder_id
        +list~str~ tags
        +bool is_locked
        +str encryption_key_ref
        +datetime created_at
        +datetime last_modified
        +__post_init__()
        +update_content(title, content)
    }
    class SecureNote {
        +lock()
        +unlock()
    }
    class NoteService {
        +create_note(title, content, folder_id, tags)
        +edit_note(note_id, title, content)
        +delete_note(note_id)
        +list_notes(folder_id, tag)
        +search_notes(query)
        +make_private(note_id)
        +make_public(note_id)
        +reveal(note, session)
        +list_versions(note_id)
        +restore_version(note_id, version_id)
    }
    class EncryptionService {
        +encrypt(plaintext) str
        +decrypt(token) str
    }
    class UserSession {
        +bool is_unlocked
        +unlock()
        +lock()
    }
    class NoteRepository {
        +save(note)
        +get(note_id)
        +load_all(folder_id, tag)
        +delete(note_id)
        +create_folder(name)
    }
    class LocalStorage {
        +query(sql, params) list~dict~
        +execute(sql, params)
    }
    class VersionHistory {
        +snapshot(note)
        +list_for(note_id)
        +get(version_id)
    }
    class SearchIndex {
        +index(note)
        +remove(note_id)
        +search(query)
    }
    class AuditLog {
        +record(action, target_note_id)
        +all()
    }

    Note <|-- SecureNote
    NoteService --> NoteRepository
    NoteService --> EncryptionService
    NoteService ..> UserSession
    NoteRepository o-- VersionHistory
    NoteRepository o-- SearchIndex
    NoteRepository o-- AuditLog
    NoteRepository --> LocalStorage
    VersionHistory --> LocalStorage
    SearchIndex --> LocalStorage
    AuditLog --> LocalStorage
```

The hollow-diamond aggregation from `NoteRepository` to `VersionHistory` is the
deliberate choice that lets version records outlive their note (FR-3 + FR-6).

For clarity the `NoteService` box shows the core note use cases; its folder/tag/move
accessors (`list_folders`, `create_folder`, `list_tags`, `move_note` — FR-7) are
elided from the diagram.

## 2. Use-case diagram

```mermaid
flowchart LR
    user(("User"))
    subgraph AstraNotes
        uc1([Create note])
        uc2([Edit note])
        uc3([Delete note])
        uc4([Search notes])
        uc5([Mark note private])
        uc6([Unlock secure notes])
        uc7([View history / restore])
        uc8([Organize: folders & tags])
        uc9([Export Markdown])
    end
    user --- uc1 & uc2 & uc3 & uc4 & uc5 & uc7 & uc8 & uc9
    uc5 -. extends .-> uc6
```

## 3. Activity diagram — Create note (FR-1, with NFR-2 failure branch)

```mermaid
flowchart TD
    A[User submits title + body] --> B{Title non-empty?}
    B -- no --> E[Flash warning · re-render editor]
    B -- yes --> C[Build Note · validate in constructor]
    C --> D[Repository.save: write notes row]
    D --> F{Storage OK?}
    F -- no --> G[Raise StorageError · flash danger]
    F -- yes --> H[Snapshot version · index for search]
    H --> I[Redirect to note view]
```

## 4. Activity diagram — Edit note (FR-2) — *resolves Week 5.2 gap*

```mermaid
flowchart TD
    A[Open note in editor] --> B[User changes title/body]
    B --> C{Locked note?}
    C -- yes --> D[Encrypt new body via EncryptionService]
    C -- no --> E[Use body as-is]
    D --> F{Title non-empty?}
    E --> F
    F -- no --> G[Flash warning · re-render]
    F -- yes --> H[update_content · bump last_modified]
    H --> I[Repository.save]
    I --> J{Storage OK?}
    J -- no --> K[StorageError · flash danger]
    J -- yes --> L[New version snapshot · redirect to view]
```

## 5. Activity diagram — Delete note (FR-3) — *resolves Week 5.2 gap*

```mermaid
flowchart TD
    A[User clicks delete] --> B{Confirm?}
    B -- no --> C[Cancel]
    B -- yes --> D{Note exists?}
    D -- no --> E[404]
    D -- yes --> F[Delete note row + note_tags]
    F --> G[SearchIndex.remove note]
    G --> H[[VersionHistory retained — no FK]]
    H --> I[Redirect to dashboard]
```

The retained-history step is the side effect the original delete model never
visualized; it is what makes a deleted note recoverable.

## 6. Activity diagram — Search (FR-4) with edge cases — *resolves Week 5.2 gap*

```mermaid
flowchart TD
    A[User enters query] --> B{Query has tokens?}
    B -- no --> C[Show all notes / prompt for a term]
    B -- yes --> D[Tokenize · build safe FTS5 MATCH]
    D --> E[Query notes_fts ORDER BY rank]
    E --> F{Any hits?}
    F -- no --> G[Show 'No notes match']
    F -- yes --> H[Show ranked results with snippets]
    note1[Locked notes are absent from the index]
    E -.-> note1
```

## 7. Deployment diagram (local-first)

```mermaid
flowchart TB
    subgraph Device["User Laptop / Desktop (single node)"]
        Browser[Web browser]
        subgraph App["AstraNotes process (Flask / Waitress)"]
            Web[web layer]
            Svc[services]
            Sto[storage]
        end
        DB[(astranotes.db — SQLite)]
        Key[[Key store: env var / instance key file]]
    end
    Browser <-->|localhost HTTP| Web
    Web --> Svc --> Sto --> DB
    Svc -. reads key .-> Key
```

Everything runs on one device. There is **no network boundary and no external
service** (NFR-1), and the encryption key is isolated from the note data — the
local-first equivalent of the original OS-keychain node.

## 8. Sequence diagram — Lock a note (FR-5)

```mermaid
sequenceDiagram
    actor U as User
    participant R as secure route
    participant S as NoteService
    participant E as EncryptionService
    participant Repo as NoteRepository
    participant A as AuditLog
    U->>R: POST /notes/{id}/lock
    R->>S: make_private(id)
    S->>E: encrypt(plaintext)
    E-->>S: ciphertext
    S->>Repo: save(SecureNote) — ciphertext at rest
    Repo->>Repo: snapshot + remove from search index
    S->>A: record("lock", id)
    S-->>R: locked note
    R-->>U: redirect to view (no plaintext rendered)
```
