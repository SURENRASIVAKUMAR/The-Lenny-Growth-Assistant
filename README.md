# The Lenny Growth Assistant
> An AI-powered advisory intelligence grounded in Lenny Rachitsky’s podcast transcripts, newsletters, and growth frameworks with a dedicated **Ship 30 for 30 Essay Writer** and live sandboxed **Artifact Viewer**.

---

## 1. Project Overview & Features

**The Lenny Growth Assistant** is a production-minded full-stack web application designed to help product managers, growth practitioners, and founders query, synthesize, and produce tactical growth assets grounded in empirical knowledge.

### Key Features:
- **Grounded Knowledge Retrieval (RAG)**: Ask questions about retention, activation, PMF engines, SaaS pricing, and team topologies. Responses provide transparent citations with speaker/guest names, source titles, URLs, and quoted snippets.
- **Dedicated Ship 30 for 30 Essay Writer**: A specialized writing engine generating structured, high-signal essays (~1,250 words) adhering to the Ship 30 for 30 methodology (Hook -> Big Idea -> Narrative Progression -> Concrete Evidence -> Tactical Playbook -> Memorable Takeaway).
- **Interactive Split-Pane Artifact Viewer**:
  - Live side-by-side rendering of Markdown documents and complete HTML/CSS web artifacts.
  - Isolated sandboxed iframe (`sandbox="allow-scripts"`) preventing untrusted HTML execution from leaking application state or cookies.
  - One-click Copy to clipboard, Download (`.md` or `.html`), and source code toggling.
- **Independent Session Management**: Multi-session isolation with persistent message histories, session renaming, and cascading deletion backed by MySQL.
- **Dual AI Provider Architecture**: Switch between local offline inference via **Ollama** and cloud inference via **OpenAI** with live diagnostics and graceful degradation.
- **Rich Dark-Mode Design System**: Hand-crafted in pure **Vanilla CSS** with deep space obsidian surfaces, indigo ambient glows, and responsive mobile/desktop layouts.

---

## 2. Technology Stack

- **Frontend**: React 18, Vite, TypeScript, Vanilla CSS (zero large frameworks or Tailwind).
- **Backend**: Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic migrations.
- **Database**: XAMPP MySQL (MariaDB 10.4) on `localhost:3306` (Database: `lenny_growth_assistant`).
- **AI Providers**: Local Ollama (`llama3:latest`) and Cloud OpenAI (`gpt-4o-mini`).
- **RAG & Search**: Configurable text chunker (500 chars / 100 overlap), local deterministic vector embeddings + cosine similarity, hybrid term scoring, and duplicate detection.

---

## 3. Database Compliance Deviation

> [!NOTE]
> **Assignment Compliance Disclosure**:
> The original assignment specification requests PostgreSQL. In the current local Windows development environment, **XAMPP MySQL** is pre-configured and active on port `3306`.
> 
> To ensure high maintainability without breaking portability:
> - All models, relationships, and queries are strictly managed through SQLAlchemy ORM and Alembic migrations.
> - Switching to PostgreSQL requires **zero modifications to application business logic**—simply update `DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/lenny_growth_assistant` in `.env` and run `alembic upgrade head`.

---

## 4. Prerequisites

1. **Python**: 3.10+ (Tested on Python 3.13.6).
2. **Node.js & npm**: Node 18+ (Tested on Node v24.18.1, npm 11.16.0).
3. **XAMPP MySQL**: Running on port `3306` with database `lenny_growth_assistant`.
4. *(Optional)* **Ollama**: For offline local inference (`http://localhost:11434`).
5. *(Optional)* **OpenAI API Key**: For cloud inference.

---

## 5. Installation & Setup

### Step 1: Clone or Navigate to Project
```bash
cd "c:\Users\Pugalarasan\OneDrive\Desktop\surenra"
```

### Step 2: Set Up Python Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\pip.exe install -r backend\requirements.txt
```

### Step 3: Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Default `.env` settings:
```ini
DB_DRIVER=mysql+pymysql
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
DB_NAME=lenny_growth_assistant

AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:latest

OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

### Step 5: Run Database Migrations
Verify MySQL is running, then apply Alembic schema:
```powershell
.\venv\Scripts\alembic.exe -c backend/alembic.ini upgrade head
```

### Step 6: Ingest Sample Knowledge Base Documents
Index the demonstration podcast transcripts and newsletter deep dives:
```powershell
.\venv\Scripts\python.exe scripts\ingest_sample_data.py
```

---

## 6. How to Run the Application

### One-Command Launcher (Recommended):
Double-click `run_app.bat` or run in PowerShell:
```powershell
.\run_app.ps1
```

### Manual Separate Commands:
**Terminal 1 (Backend API)**:
```powershell
.\venv\Scripts\uvicorn.exe backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Docs (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

**Terminal 2 (Frontend Client)**:
```powershell
cd frontend
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## 7. How to Ingest Custom Knowledge Sources

To index custom transcripts or Markdown files:
1. Place markdown files (`*.md`) into the `sample_data/` folder and re-run:
   ```powershell
   .\venv\Scripts\python.exe scripts\ingest_sample_data.py
   ```
2. Or use the in-app **Knowledge Base Explorer** modal (`+ Ingest New Document`) to paste raw text or transcripts directly through the UI.

---

## 8. Running Automated Tests

Run the complete backend test suite (15 unit and integration tests):
```powershell
.\venv\Scripts\pytest.exe backend/tests -v
```

Verify frontend production build:
```powershell
cd frontend
npm run build
```

---

## 9. 2–3 Minute Camera-On Demo Script

1. **Introduction (0:00 - 0:30)**:
   - Introduce *The Lenny Growth Assistant* as an AI advisor grounded in Lenny's podcast and newsletter content.
   - Point out the active XAMPP MySQL database and AI provider status badges in the sidebar.
2. **Knowledge Retrieval & Citations (0:30 - 1:15)**:
   - Click the prompt card: *"How do I diagnose retention issues before scaling paid acquisition?"*
   - Show the grounded response quoting Elena Verna and Casey Winters.
   - Expand the **Grounded Sources & Citations** drawer to highlight source title, guest attribution, and exact quoted snippets.
3. **Ship 30 for 30 Essay Generation (1:15 - 2:00)**:
   - Click the **Ship 30 for 30** button in the top navigation.
   - Select the topic: *"Why Activation Metrics Fail in B2B SaaS"*.
   - Click *Generate Essay Artifact*.
   - Watch the assistant formulate a ~1,250-word structured essay with Hook, Big Idea, Narrative Progression, and Takeaways.
4. **Artifact Viewer & Export (2:00 - 2:30)**:
   - Inspect the split-pane **Artifact Viewer** beside the chat.
   - Toggle between **Preview** and **Source** tabs.
   - Demonstrate the **Copy** and **Download** actions.
5. **Settings & Architecture (2:30 - 3:00)**:
   - Open the **Settings** modal to showcase the provider switcher (Ollama vs. OpenAI) and system diagnostics.
   - Conclude by highlighting the 15 passing automated tests and clean SQLAlchemy architecture.
