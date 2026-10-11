# Testing & Verification Documentation
## The Lenny Growth Assistant

---

### 1. Automated Test Commands

#### Run Full Backend Test Suite:
```powershell
# From workspace root
.\venv\Scripts\pytest.exe backend/tests/ -v
```

#### Run Strict Grounding & Provenance Tests Only:
```powershell
.\venv\Scripts\pytest.exe backend/tests/test_strict_grounding_and_provenance.py -v
```

#### Run Frontend Production Build Check:
```powershell
cd frontend
npm run build
```

---

### 2. Automated Test Results Summary (21 Passed)

| Test File | Test Case | Status | Coverage Focus |
|---|---|---|---|
| `test_strict_grounding_and_provenance.py` | `test_authoritative_sources_indexed` | **PASSED** | Verifies authoritative sources point to `episodes/*/transcript.md` |
| `test_strict_grounding_and_provenance.py` | `test_synthetic_sources_excluded_from_retrieval` | **PASSED** | Verifies `is_authoritative=False` sources are never retrieved |
| `test_strict_grounding_and_provenance.py` | `test_supported_question_grounded_answer` | **PASSED** | Supported Elena Verna query returns citations with provenance |
| `test_strict_grounding_and_provenance.py` | `test_unrelated_topic_refusal` | **PASSED** | Quantum physics query returns exact Case D limitation response |
| `test_strict_grounding_and_provenance.py` | `test_unsupported_lenny_question_refusal` | **PASSED** | Fictitious guest query returns exact Case C limitation response |
| `test_strict_grounding_and_provenance.py` | `test_ship30_unsupported_topic_limitation` | **PASSED** | Ship 30 mode explains limitation for unsupported topics |
| `test_health.py` | `test_health_endpoint` | **PASSED** | `/api/health` reports status, database type, and provider status |
| `test_health.py` | `test_config_status_endpoint` | **PASSED** | `/api/config/status` authoritative counts and flags |
| `test_sessions_and_isolation.py` | `test_session_lifecycle_and_isolation` | **PASSED** | Session CRUD, cascade deletion, and message isolation |
| `test_knowledge_and_retrieval.py` | `test_knowledge_sources_list` | **PASSED** | Knowledge sources listing and chunk counts |
| `test_knowledge_and_retrieval.py` | `test_retrieval_and_citations` | **PASSED** | Hybrid RAG retrieval, citations, and confidence flag |
| `test_knowledge_and_retrieval.py` | `test_retrieval_insufficient_evidence` | **PASSED** | Honest handling of out-of-domain queries |
| `test_artifacts.py` | `test_artifact_crud` | **PASSED** | Artifact creation, filtering, and deletion |
| `test_artifacts.py` | `test_extract_artifact_parser` | **PASSED** | Regex extraction of generated artifact blocks |
| `test_providers.py` | `test_openai_provider_missing_key` | **PASSED** | Missing API key graceful error without crash |
| `test_providers.py` | `test_ollama_provider_health_check` | **PASSED** | Ollama connection diagnostics |
| `test_providers.py` | `test_provider_factory` | **PASSED** | Dynamic provider instantiation |
| `test_ship30.py` | `test_ship30_prompt_construction` | **PASSED** | Ship 30 structural prompt generation |
| `test_ship30.py` | `test_ship30_user_prompt_with_rag` | **PASSED** | RAG context injection into essay prompts |
| `test_chat_integration.py` | `test_chat_endpoint_with_mocked_llm` | **PASSED** | Full chat lifecycle with RAG citations |
| `test_chat_integration.py` | `test_chat_ship30_mode_with_mocked_llm` | **PASSED** | Ship 30 essay generation & artifact persistence |

**Final Verification Result**: **21 passed in 7.56s**, 0 warnings, 0 failures.

---

### 3. Frontend Production Build Verification

```
> tsc -b && vite build
✓ 1916 modules transformed.
dist/index.html                   0.91 kB │ gzip:  0.50 kB
dist/assets/index-Gwj5p2Le.css   13.25 kB │ gzip:  2.98 kB
dist/assets/index-DMectn4H.js   272.09 kB │ gzip: 82.55 kB
✓ built in 1.59s
```
Zero TypeScript compiler errors (`tsc -b`). Zero bundler errors.
