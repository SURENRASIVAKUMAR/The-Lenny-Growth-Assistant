# System Architecture Documentation
## The Lenny Growth Assistant

---

### 1. High-Level Architecture Overview

```
                                    +-----------------------------------+
                                    |        React + Vite Frontend      |
                                    | (Vanilla CSS, TypeScript, Client) |
                                    +-----------------+-----------------+
                                                      |
                                             HTTP REST / JSON
                                                      |
                                    +-----------------v-----------------+
                                    |       FastAPI Application         |
                                    |  (CORS, Validation, Lifespan)     |
                                    +-----------------+-----------------+
                                                      |
                    +---------------------------------+---------------------------------+
                    |                                 |                                 |
        +-----------v-----------+         +-----------v-----------+         +-----------v-----------+
        |   Database Layer      |         |  Agent Orchestrator   |         |      RAG Engine       |
        |  SQLAlchemy + PyMySQL |         |  - Tool Dispatch      |         |  - Chunking (500/100) |
        |  Alembic Migrations   |         |  - Prompt Management  |         |  - Hybrid Retriever   |
        |  XAMPP MySQL (Port 3306)|       |  - Artifact Extractor |         |  - Vector Embeddings  |
        +-----------------------+         +-----------+-----------+         +-----------------------+
                                                      |
                                          +-----------v-----------+
                                          |  AI Provider Layer    |
                                          |  - Ollama (Local)     |
                                          |  - OpenAI (Cloud)     |
                                          +-----------------------+
```

---

### 2. Request Lifecycle

1. **User Action**: The user submits a prompt via the chat textarea or initiates a Ship 30 for 30 essay generation.
2. **REST Dispatch**: The frontend client dispatches `POST /api/chat` with `session_id`, `message`, `mode`, and optional parameters.
3. **Session Resolution**: The backend resolves or initializes a `ChatSession` record in MySQL, ensuring complete session isolation.
4. **RAG Knowledge Retrieval**:
   - The user query is tokenized and embedded.
   - The hybrid retriever executes term-overlap keyword scoring and vector cosine similarity across all indexed `document_chunks`.
   - The system checks evidence confidence. If relevant sources exceed the confidence threshold, formatted `Citation` objects are constructed.
   - If confidence is insufficient, the prompt instructs the model to explicitly state that the available sources do not support a confident answer.
5. **Prompt Assembly & Provider Invocation**:
   - In **Standard Mode**, the grounded context and user query are injected into `STANDARD_SYSTEM_PROMPT`.
   - In **Ship 30 for 30 Mode**, `build_ship30_system_prompt()` formats the prompt with the strict 6-part essay architecture, target word count (~1,250 words), and artifact container tags.
   - The active `BaseLLMProvider` (Ollama or OpenAI) is invoked asynchronously.
6. **Artifact Extraction**:
   - The response text is scanned for `<<<ARTIFACT:TYPE:title="..." >>> ... <<<END_ARTIFACT>>>` blocks.
   - Extracted artifacts are saved to the `artifacts` table linked to the active session.
7. **Message Persistence & Delivery**:
   - The assistant message (with citations and model metadata) is persisted to the `messages` table.
   - The structured `ChatResponse` is returned to the frontend, updating the conversation stream and automatically displaying the new artifact in the Artifact Viewer.

---

### 3. Database Schema & Compliance Deviation

#### Compliance Note: MySQL vs. PostgreSQL
The assignment specification outlines PostgreSQL as the reference database. Due to the local development environment using XAMPP MySQL (MariaDB 10.4 on port 3306), this application is implemented using MySQL via the pure-Python driver `pymysql`. 

**Portability Architecture**:
All database interactions are strictly mediated through the SQLAlchemy ORM (`Base = declarative_base()`) and Alembic migrations. No raw database-specific SQL dialect is used in business logic. Switching to PostgreSQL requires only:
1. Setting `DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname` in `.env`.
2. Running `alembic upgrade head`.
Zero Python application code requires modification.

#### Schema Overview:
- `chat_sessions`: `id` (PK, UUID), `title`, `created_at`, `updated_at`.
- `messages`: `id` (PK, UUID), `session_id` (FK -> chat_sessions, CASCADE), `role`, `content`, `model_used`, `provider_used`, `citations` (JSON text), `created_at`.
- `knowledge_sources`: `id` (PK, UUID), `title`, `source_type`, `url`, `author_or_guest`, `summary`, `status`, `chunk_count`, timestamps.
- `document_chunks`: `id` (PK, UUID), `source_id` (FK -> knowledge_sources, CASCADE), `chunk_index`, `content`, `token_count`, `metadata_json`, `embedding` (vector text), timestamps. Indexed on `(source_id, chunk_index)`.
- `artifacts`: `id` (PK, UUID), `session_id` (FK -> chat_sessions, CASCADE), `title`, `artifact_type`, `content`, `metadata_json`, timestamps.

---

### 4. Security Architecture

1. **Sandboxed HTML Preview**: HTML artifacts render inside an iframe configured with `sandbox="allow-scripts"`. The absence of `allow-same-origin` ensures that generated scripts cannot read `localStorage`, cookies, session tokens, or parent window variables.
2. **SQL Injection Prevention**: 100% of queries use SQLAlchemy parameter binding and ORM filters.
3. **Secret Isolation**: `OPENAI_API_KEY` and database passwords reside strictly in backend environment variables. The `/api/config/status` endpoint only transmits boolean flags (`openai_configured: true`), never raw keys.
4. **Controlled Tools**: Agent tools cannot execute arbitrary terminal commands, access arbitrary filesystem directories, or execute raw database DDL.
