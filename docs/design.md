# Design System & UI Architecture
## The Lenny Growth Assistant

---

### 1. Design Philosophy & Aesthetic Principles
The Lenny Growth Assistant interface is built around four central aesthetic tenets:
1. **Curated Dark Mode Elegance**: Built upon deep space obsidian (`#0a0d14` and `#0f1422`) with subtle violet/indigo ambient radial glows (`rgba(99, 102, 241, 0.08)`) and high-contrast, readable slate typography (`#f8fafc`).
2. **Glassmorphism & Surface Depth**: Cards and message bubbles use semi-translucent backdrops with 1px border highlights (`rgba(255, 255, 255, 0.08)`) and soft depth shadows.
3. **Information Grounding & Transparency**: Citations, model badges, and execution providers are immediately legible without cluttering the primary conversation.
4. **Zero-Framework Vanilla CSS**: Implemented entirely in Vanilla CSS for maximal speed, precision control, zero CSS bloat, and guaranteed long-term maintainability.

---

### 2. Design System Tokens

#### Color Palette
- **Background Primary**: `#0a0d14` (Deep Space Obsidian)
- **Background Secondary**: `#0f1422` (Sidebar & Panels)
- **Background Tertiary**: `#161c30` (Interactive surfaces & inputs)
- **Accent Primary**: `#6366f1` (Indigo Glow)
- **Accent Secondary**: `#8b5cf6` (Electric Violet)
- **Accent Gradient**: `linear-gradient(135deg, #6366f1 0%, #a855f7 100%)`
- **Ship 30 Gold Gradient**: `linear-gradient(135deg, #f59e0b 0%, #d97706 100%)`
- **Text Main**: `#f8fafc` (Slate 50)
- **Text Secondary**: `#94a3b8` (Slate 400)
- **Text Muted**: `#64748b` (Slate 500)
- **Success / Online**: `#10b981` (Emerald 500)
- **Warning**: `#f59e0b` (Amber 500)
- **Error / Offline**: `#ef4444` (Rose 500)

#### Typography System
- **Primary Typeface**: `Inter`, sans-serif (imported via Google Fonts with preconnect headers)
- **Code & Artifact Typeface**: `JetBrains Mono`, `Fira Code`, monospace
- **Scale**:
  - Display / H1: 1.5rem (24px), font-weight 700
  - Section / H2: 1.25rem (20px), font-weight 600
  - Card Heading / H3: 1.05rem (17px), font-weight 600
  - Body Text: 0.92rem (14.7px), line-height 1.6
  - Caption / Badges: 0.74rem (11.8px), font-weight 500

---

### 3. Layout Architecture & Workspace Panels

```
+---------------------------------------------------------------------------------------+
|  Sidebar (280px)   |  Top Navigation Bar (Height: 60px)                               |
|                    +-----------------------------------+------------------------------+
|  [Logo & Brand]    |  Chat Stream Area (52%)           |  Artifact Viewer (48%)       |
|  [+ New Chat]      |                                   |                              |
|                    |  User Messages (Indigo bubble)    |  [Header & Tab Bar]          |
|  Session List:     |  Assistant Messages (Obsidian)    |  - Preview (Sandbox / MD)    |
|  - Active Chat     |  Inline Citations Cards           |  - Source (Raw Monospace)    |
|  - Prior Session   |                                   |  [Copy] [Download] [Close]   |
|                    |  Empty State: 4 Prompt Cards      |                              |
|                    +-----------------------------------+------------------------------+
|  [DB Status Badge] |  Chat Input Box (Shift+Enter / Send)                             |
|  [AI Model Badge]  |  [Mode Badge: Ship 30 for 30 / Standard]                         |
+--------------------+------------------------------------------------------------------+
```

---

### 4. Key UI States & Micro-Interactions

1. **Empty Conversation State**:
   - Centered glowing hero icon with welcoming copy.
   - 4 clickable discovery cards (Retention & Activation, PMF Four Fits, SaaS Value Metrics, PM Archetypes). Clicking instantly populates and submits the query.
2. **Streaming & Ingestion Loading**:
   - Pulse animation on the emerald status indicator with status update ("Searching knowledge base and formulating grounded answer...").
3. **Citations Accordion**:
   - Expandable drawer nested below assistant responses. Shows guest names, external hyperlinks, and exact quoted snippets.
4. **Artifact Split-Screen**:
   - Smooth slide-in split panel on the right. When multiple artifacts exist in a session, a selector dropdown lets the user switch between them seamlessly.
5. **Sandboxed HTML Preview**:
   - Isolated iframe embedded with `sandbox="allow-scripts"` to safely preview generated HTML layouts and prototypes without risking parent context leak.
