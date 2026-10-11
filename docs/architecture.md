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
        |  PostgreSQL (Primary) |         |  - Strict Grounding   |         |  - Authoritative Repo |
        |  SQLAlchemy + psycopg2|         |  - Guard Refusals     |         |  - Provenance Tracking|
        |  Alembic Migrations   |         |  - Artifact Extractor |         |  - Hybrid Vector/KW   |
        |  MySQL (Preserved)    |         +-----------+-----------+         |  - Min Threshold Check|
        +-----------------------+                     |                     +-----------------------+
                                          +-----------v-----------+
                                          |  AI Provider Layer    |
                                          |  - Demo Synthesizer   |
                                          |  - Ollama (Local)     |
                                          |  - OpenAI (Cloud)     |
                                          +-----------------------+
```

---

### 2. Request Lifecycle & Strict Grounding Policy

1. **User Action**: The user submits a prompt via the chat textarea or initiates a Ship 30 for 30 essay generation.
2. **REST Dispatch**: The frontend client dispatches `POST /api/chat` with `session_id`, `message`, `mode`, and optional parameters.
3. **Session Resolution**: The backend resolves or initializes a `ChatSession` record in the database, ensuring complete session isolation.
4. **Authoritative RAG Retrieval**:
   - The user query is tokenized and embedded.
   - The hybrid retriever executes term-overlap keyword scoring and vector cosine similarity across only authoritative chunks (`is_authoritative == True`).
   - Synthetic demo documents are excluded from production retrieval.
   - The system checks evidence confidence against `MIN_EVIDENCE_THRESHOLD` (0.25).
5. **Strict Grounding Enforcement (Pre-Inference Gate)**:
   - **Case A (Sufficient Evidence)**: Proceed to answer generation, passing retrieved context with real provenance paths.
   - **Case C (Insufficient Evidence for Lenny Topic)**: Answer generation is **blocked**. Assistant returns:
     *"I couldn't find sufficient supporting information for this question in the indexed Lenny’s Podcast / Newsletter repository. I can answer only when the available source material supports the response."*
   - **Case D (Unrelated Topic)**: Answer generation is **blocked**. Assistant returns:
     *"I don't have sufficient information about this topic in the specified Lenny’s Podcast / Newsletter repository to provide a source-grounded answer."*
   - **Ship 30 Essay with Insufficient Evidence**: Discloses limitations rather than fabricating claims.
6. **Provider Execution**:
   - For grounded queries, `DemoSynthesizerProvider`, `OllamaProvider`, or `OpenAIProvider` synthesizes structured answers with citations.
7. **Artifact Extraction & Persistence**:
   - Artifact blocks are extracted, saved to the `artifacts` table, and returned for split-pane live viewing.

---

### 3. Database Layer: PostgreSQL Primary & Safe MySQL Migration

- **Primary Database**: PostgreSQL via `postgresql+psycopg2` / `postgresql+psycopg` on port `5432`.
- **Legacy Preservation**: The original MySQL database on port `3306` is preserved untouched.
- **Repeatable Migration Script**: `scripts/migrate_mysql_to_postgres.py` connects to MySQL, connects to PostgreSQL, creates the target schema, transfers all tables (`chat_sessions`, `messages`, `artifacts`, `knowledge_sources`, `document_chunks`), and validates row counts and foreign keys.

---

### 4. Authoritative Knowledge Source: ChatPRD Transcripts

- **Source Repository**: `https://github.com/ChatPRD/lennys-podcast-transcripts` (303 total episodes).
- **Provenance Tracking**: Every chunk retains `provenance_file` pointing to the exact relative markdown file (e.g. `episodes/elena-verna/transcript.md`).
- **Metadata**: Retains guest names, YouTube URLs, episode duration, and publication dates.
- **Repeatable Ingestion**: `scripts/ingest_authoritative_transcripts.py`.
