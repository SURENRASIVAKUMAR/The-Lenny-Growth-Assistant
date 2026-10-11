# Product Requirements Document (PRD)
## Project: The Lenny Growth Assistant

---

### 1. Problem Statement
Product managers, founders, and growth leads face a deluge of tactical advice spread across hundreds of hours of podcast episodes, interviews, and newsletter deep dives. When attempting to solve acute operational challenges—such as fixing a leaky retention bucket, choosing a SaaS value metric, structuring empowered product trios, or measuring product-market fit—operators struggle to quickly locate authoritative, grounded frameworks. 

Existing generic AI chatbots frequently hallucinate quotes, invent podcast episodes, and deliver bland, cliché-ridden responses without verifiable attribution. Furthermore, operators lack an integrated workspace to convert these grounded insights into structured essays, execution playbooks, and interactive web artifacts.

---

### 2. Goals & Objectives
1. **Grounded Retrieval (RAG)**: Deliver answers firmly rooted in Lenny Rachitsky's podcast interviews and newsletter archives, accompanied by verifiable citations (guest name, source title, snippet, and link).
2. **Honest Confidence Boundaries**: Explicitly disclose when the indexed knowledge base lacks sufficient evidence to answer a question, avoiding fabricated claims.
3. **Dedicated "Ship 30 for 30" Writing Skill**: Provide a dedicated writing engine that converts knowledge base insights into structured, compelling essays of approximately 1,250 words following the Ship 30 for 30 methodology (Hook -> Big Idea -> Narrative Progression -> Evidence -> Actionable Playbook -> Memorable Takeaway).
4. **Live Artifact Generation & Sandboxed Viewing**: Enable users to view, copy, download, and render generated Markdown documents and secure HTML/CSS web artifacts side-by-side with the chat.
5. **Multi-Model Flexibility**: Allow seamless switching between local inference (Ollama) and cloud inference (OpenAI) with clear configuration warnings and no hard failure crashes when keys are missing.
6. **Session Isolation & Persistence**: Maintain independent, persistent chat sessions and artifact histories backed by a relational database.

---

### 3. User Personas
1. **The Early-Stage Founder**: Needs fast, battle-tested heuristics on finding Product-Channel Fit and establishing the Sean Ellis PMF survey benchmark.
2. **The Senior Product Manager / Growth Lead**: Seeks actionable activation formulas and pricing playbook comparisons from industry leaders like Casey Winters, Elena Verna, and Patrick Campbell.
3. **The Content Creator / Product Essayist**: Uses the Ship 30 for 30 essay writer to draft authoritative thought leadership essays grounded in real empirical frameworks.

---

### 4. Functional Requirements

#### A. Chat & Conversation Management
- **FR-1.1**: Users can create, switch between, rename, and delete independent chat sessions.
- **FR-1.2**: Deleting a session cascades cleanly to remove associated messages and artifacts.
- **FR-1.3**: Messages support markdown formatting, inline citation badges, and model attribution tags.
- **FR-1.4**: Chat area provides responsive mobile and desktop viewports, Enter-to-send, and Shift+Enter for newlines.
- **FR-1.5**: Empty state displays high-signal prompt cards to guide first-time users.

#### B. Knowledge Base & Retrieval-Augmented Generation (RAG)
- **FR-2.1**: Support ingestion of Markdown, plain text, and podcast transcript documents.
- **FR-2.2**: Text chunking with configurable overlap (default 500 chars / 100 overlap) respecting paragraph and sentence boundaries.
- **FR-2.3**: Hybrid retrieval combining keyword matching and vector cosine similarity.
- **FR-2.4**: Every response backed by the knowledge base must display source titles, guest/author names, URLs, and verbatim snippets.
- **FR-2.5**: Built-in duplicate detection and knowledge base refresh endpoint.

#### C. Dedicated Ship 30 for 30 Writing Skill
- **FR-3.1**: Dedicated writing trigger modal allowing customization of Topic, Audience, Tone, and Target Word Count (~1,250 words).
- **FR-3.2**: Follows strict structural constraints: Hook, Central Idea, 3-5 Punchy Headings, Concrete Evidence, Actionable Playbook, and Memorable Takeaway.
- **FR-3.3**: Automatic encapsulation of essays inside Artifact containers for immediate viewer extraction.

#### D. Artifact Generation & Sandboxed Viewer
- **FR-4.1**: Automatic detection and extraction of generated Markdown, HTML, and Essay artifacts.
- **FR-4.2**: Split-pane interface allowing simultaneous chat and artifact inspection.
- **FR-4.3**: HTML artifacts render inside a sandboxed iframe (`sandbox="allow-scripts"` without same-origin privileges).
- **FR-4.4**: One-click actions to Copy raw content, Download as `.md` or `.html`, and switch between multiple session artifacts.

#### E. AI Provider & Health Management
- **FR-5.1**: Clean abstraction supporting Local Ollama (`llama3:latest`) and Cloud OpenAI (`gpt-4o-mini`).
- **FR-5.2**: System health endpoint reporting database connectivity and provider availability.
- **FR-5.3**: Missing API keys or offline local services fail gracefully with actionable diagnostic messages.

---

### 5. Non-Functional Requirements
- **NFR-1 (Security)**: Sandboxed iframe execution, environment-based credentials, no secrets exposed in frontend bundles or logs.
- **NFR-2 (Performance)**: Hybrid search and local embedding generation executes in under 200ms per query.
- **NFR-3 (Reliability)**: Connection pooling with `pool_pre_ping` to handle idle database disconnects gracefully.
- **NFR-4 (Portability)**: SQLAlchemy ORM layer isolated such that switching from MySQL to PostgreSQL requires only updating `DATABASE_URL`.

---

### 6. Out-of-Scope (V1)
- Scraping third-party paid Substack archives directly (all source ingestion is done via authorized local files or API ingestion).
- Multi-user authentication/SSO (designed for single-tenant local internship deployment).
