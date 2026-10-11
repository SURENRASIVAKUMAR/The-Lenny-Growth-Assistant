# Agent Execution Transcripts & Execution Logs
## The Lenny Growth Assistant

This document contains representative execution traces and verified test outputs from the agent orchestration and RAG retrieval pipeline.

---

### Example 1: Grounded Knowledge Retrieval & Citations

**User Request**:
> "What is the fundamental law of retention according to Elena Verna, and how should early stage teams calculate their activation milestone?"

**Execution Steps**:
1. **Request Intake**:
   - Route: `POST /api/chat`
   - Mode: `standard`
   - Session: Auto-created `ChatSession(id='3a89e9f1-7c9b-43ad-8d7b-bf0d8c2e1f40')`
2. **Tool / RAG Invocation**:
   - Function: `retrieve_relevant_chunks(query, db, top_k=4)`
   - Chunks matched: 3 chunks from `sample_data/01_retention_and_activation_deepdive.md`
   - Max hybrid relevance score: `0.78` (Evidence Confidence: **TRUE**)
3. **Citations Generated**:
   - `Source`: "Demonstration Document: Lenny Growth Deep Dive on Retention and User Activation"
   - `Author/Guest`: "Casey Winters & Elena Verna (Growth Advisors)"
   - `URL`: `https://www.lennysnewsletter.com/p/retention-and-activation-guide`
   - `Snippet`: "Retention is the single most important metric for any consumer or B2B SaaS product. If your retention curve does not flatten parallel to the x-axis, you do not have a leaky bucket—you have a bucket with no bottom..."
4. **Model Invoked**:
   - Provider: `ollama` (or `openai` when configured)
   - Model: `llama3:latest`
5. **Final Output Formatted**:
   - Direct synthesized answer referencing Elena Verna's "bucket with no bottom" principle and Casey Winters' 7-day correlation formula.
   - Inline citation drawer populated with source cards.

---

### Example 2: Out-of-Domain Query (Insufficient Evidence Handling)

**User Request**:
> "What are the latest findings regarding quantum gravity tensor perturbations in cosmological inflation?"

**Execution Steps**:
1. **Request Intake**:
   - Route: `POST /api/chat`
   - Mode: `standard`
2. **Tool / RAG Invocation**:
   - Function: `retrieve_relevant_chunks(query, db, top_k=4)`
   - Chunks matched: 0 relevant chunks (Max hybrid relevance score: `0.02`)
   - Evidence Confidence: **FALSE**
3. **Prompt Instruction Applied**:
   - System prompt detects `has_evidence == False`.
   - Explicit guardrail activated:
   > "Based on the currently indexed knowledge base, there is insufficient evidence to answer this question accurately."
4. **Result**:
   - The model refrains from hallucinating podcast episodes with theoretical physicists, stating honest limitations.

---

### Example 3: Dedicated "Ship 30 for 30" Essay Writer with Artifact Generation

**User Request**:
> "Write a Ship 30 for 30 essay on: The Hidden Per-Seat Pricing Trap in Collaborative Products"

**Execution Steps**:
1. **Request Intake**:
   - Mode: `ship30`
   - Target Length: `1250` words
   - Audience: "Product managers, founders, and growth leaders"
   - Tone: "Authoritative, tactical, conversational, and analytical"
2. **RAG Context Retrieval**:
   - Matched: `sample_data/03_pricing_and_packaging_frameworks.md` (Patrick Campbell & Madhavan Ramanujam on value metrics and the per-seat trap).
3. **Prompt Assembly**:
   - `build_ship30_system_prompt()` applied with 6 structural elements: Hook, The One Big Idea, Narrative Progression, Concrete Evidence, Actionable Playbook, Memorable Takeaway.
   - Enclosed inside artifact tags: `<<<ARTIFACT:ESSAY:title="The Hidden Per-Seat Pricing Trap">>> ... <<<END_ARTIFACT>>>`
4. **Artifact Extractor**:
   - Extractor regex triggered.
   - Artifact saved to database:
     - `table`: `artifacts`
     - `title`: "The Hidden Per-Seat Pricing Trap"
     - `artifact_type`: `essay`
     - `session_id`: linked to active conversation.
5. **Frontend Response**:
   - Chat area displays summary: *"Created artifact: **The Hidden Per-Seat Pricing Trap** (ESSAY) — Viewable in the Artifact Viewer panel."*
   - Artifact Viewer panel automatically opens on the right side of the screen displaying the formatted Markdown essay with Copy and Download actions.

---

### Example 4: Provider Fallback & Offline Diagnostics

**Scenario**:
- Primary provider set to `openai` without an `OPENAI_API_KEY` present in `.env`.
- User dispatches a message.
- Provider layer catches `ValueError: OpenAI is not configured. Please supply OPENAI_API_KEY in .env or switch to Ollama local inference.`
- Application reports clean HTTP 400 error banner with dismissible button rather than crashing the server or hanging indefinitely.
- Switching to Ollama or adding the key in Settings resolves the issue immediately.
