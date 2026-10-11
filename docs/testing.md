# Testing & Verification Documentation
## The Lenny Growth Assistant

---

### 1. Automated Test Commands

#### Run Backend Test Suite:
```powershell
# From workspace root
.\venv\Scripts\pytest.exe backend/tests -v
```

#### Run Frontend Production Build Check:
```powershell
# From workspace root
cd frontend
npm run build
```

---

### 2. Automated Test Results Summary

| Test File | Test Case | Status | Coverage Focus |
|---|---|---|---|
| `test_health.py` | `test_health_endpoint` | **PASSED** | `/api/health` status and database connection |
| `test_health.py` | `test_config_status_endpoint` | **PASSED** | `/api/config/status` diagnostic data |
| `test_sessions_and_isolation.py` | `test_session_lifecycle_and_isolation` | **PASSED** | Session CRUD, cascade deletion, and message isolation |
| `test_knowledge_and_retrieval.py` | `test_knowledge_sources_list` | **PASSED** | Knowledge sources listing and metadata |
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

**Result: 15 passed in 9.32s, 0 warnings, 0 failures.**

---

### 3. Manual UI Test Checklist

- [x] **New Session Creation**: Click "+ New Conversation" in the sidebar; verifies an empty chat stream with prompt suggestions is rendered.
- [x] **Rename Session**: Click pencil icon next to session in sidebar; enter new title and press Enter; verifies title updates immediately and persists across refresh.
- [x] **Delete Session**: Click trash icon; confirms dialog; verifies session and associated messages are removed from MySQL.
- [x] **Ask Grounded Question**: Submit "What is the fundamental law of retention according to Elena Verna?"; verifies response includes inline citations drawer.
- [x] **Citations Drawer**: Click "Grounded Sources & Citations"; verifies source title, guest name ("Elena Verna"), and quoted snippet appear.
- [x] **Ship 30 for 30 Essay**: Click "Ship 30 for 30" button in header; select suggested topic or customize parameters; submit; verifies generated essay opens automatically in the Artifact Viewer.
- [x] **Artifact Preview & Source**: Toggle between "Preview" and "Source" tabs in Artifact Viewer; verifies clean typography and raw markdown view.
- [x] **Artifact Copy & Download**: Click copy button (displays green checkmark feedback); click download button (downloads `.md` or `.html` file).
- [x] **Knowledge Base Explorer**: Click "Knowledge" in header; verifies list of 4 indexed sources and 27 chunks.
- [x] **Settings & Diagnostics**: Click "Settings" in header; inspects MySQL status, Ollama status, and OpenAI configuration flags.
