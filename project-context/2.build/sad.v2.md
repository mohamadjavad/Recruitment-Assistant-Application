# System Architecture Document (SAD) v2 — Phase 3: Post-MVP

## Recruitment Assistant Application — CrewAI Multi-Agent System

**Document Version:** 2.0  
**Date:** July 8, 2026  
**Prepared by:** @system.arch (AAMAD Phase 3 — Deliver)  
**Input Sources:** sad.md (v1.0), phase-3-outline.md, prd.md, mrd.md, architecture-plan.md, qa-plan.md, integration-notes.md, technical-debt.md, frontend-plan.md  
**AAMAD_TARGET_RUNTIME:** crewai

---

## 1. Phase 3 Architecture Overview

### 1.1 Phase Transition from MVP

Phase 2 (Build) delivered the MVP CLI application (v0.1.0) — a Python-based CrewAI sequential workflow with 4 agents, file-based output, and no persistent storage. The application runs locally via `uv run recruitment`, accepts a job description, executes a 4-agent pipeline (Researcher → Matcher → Communicator → Reporter), and produces `candidate_report.md`.

Phase 3 (Post-MVP Delivery) evolves this foundation across 5 version increments, each building on the previous without breaking changes. The architecture transitions from a single-process CLI tool to a multi-tier web application with database persistence, ATS integration, hierarchical agent orchestration, and production deployment infrastructure.

| Aspect | MVP (v0.1.0) | Phase 3 Target (v1.0.0) |
|--------|--------------|-------------------------|
| **Interface** | Python CLI (Rich library) | Next.js Web UI + CLI coexisting |
| **Agent Process** | Sequential (4 agents) | Hierarchical with Manager Agent |
| **Data Storage** | File-based (`candidate_report.md`) | SQLite → PostgreSQL |
| **Auth** | None (single-user local) | Clerk/Auth0 multi-tenancy |
| **ATS Integration** | None | Greenhouse, Lever adapters |
| **Analytics** | None | Dashboard with execution history |
| **Deployment** | Local `uv run` | Docker + Kubernetes |
| **CI/CD** | None | GitHub Actions → Docker Registry |
| **Streaming** | Simulated spinners (QA-01) | SSE real-time from CrewAI |
| **LLM Config** | .env manual setup (QA-02) | Web UI interactive wizard |

### 1.2 Design Principles for Phase 3

1. **Incremental Evolution**: Each version (v0.2.0 → v1.0.0) adds capabilities while maintaining backward compatibility. The CLI continues to function as Phase 3 features are added (Strangler Fig pattern — SAD v1 §3.4).

2. **Clean Architecture Separation**: Frontend (Next.js) and Backend (Python CrewAI) communicate through a defined API layer. The Next.js app does NOT import Python modules directly — it spawns subprocesses or communicates via HTTP/SSE.

3. **Streaming-First UX**: Real-time agent progress via Server-Sent Events (SSE) replaces the simulated spinners (fixes QA-01 — SAD v1 §3.3, qa-plan.md §5.2). Users see actual agent state transitions, task completion, and intermediate outputs.

4. **Persistence as Foundation**: SQLite database introduced in v0.5.0 powers all analytics queries and execution history. The schema is designed with migration in mind — PostgreSQL upgrade path via Alembic.

5. **Graduated Production Readiness**: Each version adds production concerns in deliberate order: CI/CD (v0.2.0) → ATS integration security (v0.3.0) → performance (v0.4.0) → observability (v0.5.0) → auth/compliance (v1.0.0).

6. **Plugin Architecture for Integrations**: ATS adapters use a provider-agnostic interface (v0.3.0). Adding a new ATS requires only implementing the adapter contract — no changes to agent logic.

### 1.3 Version Roadmap

| Version | Features | Effort | Dependencies | PRD Reference |
|---------|----------|--------|--------------|---------------|
| v0.1.0 | CLI MVP (already delivered) | — | — | PRD §8.1 |
| v0.2.0 | Web Chat UI (Next.js + assistant-ui + shadcn/ui + SSE) | 5-10 days | None (foundation) | PRD §8.2 (F-023) |
| v0.2.1 | Polish pass: QA-01/02/04 fixes, interactive wizard | 2-3 days | v0.2.0 | qa-plan §5, §7.1 |
| v0.3.0 | ATS Integration (Greenhouse, Lever adapters) | 10-15 days | OAuth partnerships | PRD §8.2, MRD §4 |
| v0.4.0 | Multi-Role Hiring + Hierarchical Process | 5-8 days | v0.2.0 UI foundation | PRD §8.2, SAD v1 §1.2 |
| v0.5.0 | Analytics Dashboard + SQLite Database | 8-10 days | Database schema | PRD §8.2, PRD §5.1 |
| v1.0.0 | Auth, Multi-Tenancy, Docker, Kubernetes | 10-15 days | v0.5.0 analytics | PRD §8.2, technical-debt.md |

**Source**: phase-3-outline.md §1, PRD §8.2, technical-debt.md §2

---

## 2. Architecture Evolution Across Versions

This section shows how the architecture evolves incrementally from MVP through each Phase 3 version. Each version's architecture section (Sections 3-7) provides the detailed component design.

```
v0.1.0 (MVP)
┌─────────────────────────────────────────────────────────┐
│  [CLI] ←──→ [main.py] ←──→ [RecruitmentCrew]          │
│                               Sequential 4-agent        │
│                               File-based output         │
└─────────────────────────────────────────────────────────┘

v0.2.0 (Web UI)
┌─────────────────────────────────────────────────────────┐
│  [Browser] ←WS→ [Next.js API] ←subprocess→ [CrewAI]  │
│  [CLI] continues to work alongside                      │
│  [assistant-ui] + [shadcn/ui] + [Tailwind CSS]          │
└─────────────────────────────────────────────────────────┘

v0.3.0 (ATS Integration)
┌─────────────────────────────────────────────────────────┐
│  [CrewAI] ←→ [ATS Adapter Interface]                    │
│                    ├── [GreenhouseAdapter] ←OAuth→ [GH]  │
│                    └── [LeverAdapter]    ←OAuth→ [Lever] │
└─────────────────────────────────────────────────────────┘

v0.4.0 (Hierarchical Process)
┌─────────────────────────────────────────────────────────┐
│  [Manager Agent] delegates to sub-crews                 │
│   ├── [Sub-Crew A: Researcher→Matcher→Comm→Reporter]    │
│   ├── [Sub-Crew B: Researcher→Matcher→Comm→Reporter]    │
│   └── [Sub-Crew C: Researcher→Matcher→Comm→Reporter]    │
└─────────────────────────────────────────────────────────┘

v0.5.0 (Database + Analytics)
┌─────────────────────────────────────────────────────────┐
│  [CrewAI] ←→ [SQLAlchemy ORM] ←→ [SQLite Database]      │
│  [Next.js Dashboard] queries DB for analytics           │
└─────────────────────────────────────────────────────────┘

v1.0.0 (Production)
┌─────────────────────────────────────────────────────────┐
│  [Docker Container] → [Kubernetes Pod]                   │
│  [Clerk Auth] → [Multi-Tenant RBAC]                     │
│  [PostgreSQL] ← migration from SQLite                   │
└─────────────────────────────────────────────────────────┘
```

Each version inherits all capabilities from prior versions. The Strangler Fig pattern ensures the CLI (v0.1.0) continues to work even as the web UI grows alongside it.

---

## 3. v0.2.0 — Web Chat UI Architecture

### 3.1 High-Level Architecture

```
┌──────────────────────┐     ┌──────────────────────────────────┐
│     Browser          │     │       Next.js Application         │
│                      │     │                                  │
│  ┌────────────────┐  │     │  ┌────────────────────────────┐  │
│  │ assistant-ui   │  │     │  │  App Router                │  │
│  │  <Thread>      │  │     │  │                            │  │
│  │  <Message>     │  │SSE  │  │  /api/chat         POST    │  │
│  │  <Composer>    │◄─┼─────┼──┤  /api/chat/status  GET     │  │
│  │  <ToolOutput>  │  │     │  │  /dashboard        GET     │  │
│  └────────────────┘  │     │  └───────────┬────────────────┘  │
│                      │     │              │                    │
│  ┌────────────────┐  │     │  ┌───────────▼────────────────┐  │
│  │ Zustand Store  │  │     │  │  Python Subprocess Layer   │  │
│  │ (session, msgs)│  │     │  │                            │  │
│  └────────────────┘  │     │  │  child_process.spawn(      │  │
│                      │     │  │    "uv", "run",            │  │
│  ┌────────────────┐  │     │  │    "recruitment", "--sse"  │  │
│  │ shadcn/ui      │  │     │  │  )                         │  │
│  │ components     │  │     │  │                            │  │
│  └────────────────┘  │     │  │  stdout → SSE events       │  │
│                      │     │  └────────────────────────────┘  │
└──────────────────────┘     └──────────────────────────────────┘
                                              │
                                              ▼
                                   ┌──────────────────────────┐
                                   │  Python CrewAI Process   │
                                   │                          │
                                   │  RecruitmentCrew         │
                                   │   .kickoff()             │
                                   │                          │
                                   │  4 agents (sequential)   │
                                   │                          │
                                   │  Output: report string   │
                                   └──────────────────────────┘
```

**Source**: PRD §4.7 (F-023), PRD §8.2, phase-3-outline.md §2, SAD v1 §3.4

### 3.2 Technology Stack

| Layer | Component | Technology | Version | Purpose |
|-------|-----------|------------|---------|---------|
| Frontend | Framework | Next.js (App Router) | Latest | Server-rendered React, API routes |
| Frontend | UI Kit | assistant-ui | Latest | Chat thread, messages, composer |
| Frontend | Design System | shadcn/ui | Latest | Accessible component primitives |
| Frontend | Styling | Tailwind CSS v4 | v4 | Utility-first CSS |
| Frontend | State | Zustand | Latest | Lightweight client state |
| Frontend | Streaming | EventSource (native SSE) | Built-in | Real-time agent progress |
| Backend | API Layer | Next.js API Routes | Built-in | BFF proxy to Python |
| Backend | Runtime | Python + CrewAI | >=1.15.1 | Agent orchestration |
| Backend | Process Mgmt | Node `child_process` | Built-in | Spawn Python subprocess |
| Dev | CI/CD | GitHub Actions | — | ruff + mypy + pytest |

**Source**: phase-3-outline.md §2, PRD §7.3 (F-023), SAD v1 §3.4

### 3.3 Component Architecture

#### 3.3.1 Chat Interface (assistant-ui)

The chat interface uses assistant-ui's declarative component model:

| Component | Purpose | Implementation Notes |
|-----------|---------|---------------------|
| `<Thread>` | Container for message list + composer | Manages scroll, auto-scroll on new content |
| `<Message>` | Renders individual agent/user messages | Supports markdown rendering for reports |
| `<Composer>` | Text input + send button | Submits job descriptions |
| `<ToolOutput>` | Renders agent tool usage (future) | Placeholder for v0.4.0+ agent actions |

The chat interface is augmented with shadcn/ui components for:
- **Job Description Form**: Structured `<Form>` with `<Input>`, `<Textarea>`, `<Select>` fields that convert structured input into a natural-language job description for the agent backend (PRD §4.2).
- **Agent Status Panel**: A `<Card>` or `<Panel>` showing real-time agent state (name, task, progress %) sourced from SSE events.
- **Report View**: Toggle between raw markdown and rendered HTML views of the final candidate report.

#### 3.3.2 SSE Streaming Service

The SSE streaming service is a Next.js API route (`/api/chat`) that:

1. Receives the job description JSON via POST
2. Spawns a Python subprocess (`uv run recruitment --sse`)
3. Pipes the Python's stdout line-by-line
4. Parses structured JSON events from stdout
5. Streams SSE events back to the browser client
6. Handles process cleanup on client disconnect

#### 3.3.3 Agent Status Panel

Fixes **QA-01** (qa-plan.md §5.1, qa-plan.md §7.1). The simulated progress spinner in the CLI (main.py:373-379) is replaced by real-time agent state from the CrewAI process. The Python backend emits structured JSON events at each agent lifecycle transition:

```
agent_start    → Panel shows "Researcher is working..."
agent_complete → Panel shows "Researcher done!" + output summary
task_progress  → Panel updates progress percentage
```

#### 3.3.4 Interactive Setup Wizard

Fixes **QA-02** (qa-plan.md §5.1, qa-plan.md §7.1). On first launch (or when API keys are missing), the Next.js app displays an interactive setup wizard:

1. Welcome screen explaining the tool
2. API key input fields (LLM provider, Serper.dev)
3. LLM provider selection dropdown (GLM-5.2, OpenAI, Ollama, custom)
4. Test connection button to validate configuration
5. Auto-generation of `.env` file or secure session storage

### 3.4 Data Flow

**End-to-end flow from user input to report display:**

```
Step 1: User pastes job description → POST /api/chat
Step 2: Next.js API route validates input (same rules as main.py validate_job_description)
Step 3: API route writes job_requirements to a temporary JSON file
Step 4: API route spawns: child_process.spawn("uv", ["run", "recruitment", "--sse", "--input", tmpfile])
Step 5: Python process reads input file, runs crew.kickoff(job_requirements)
Step 6: Python emits structured JSON events to stdout:
        {"event": "agent_start", "agent": "Researcher", "task": "TASK-01"}
        {"event": "agent_complete", "agent": "Researcher", "output": "...", "duration": 45}
        {"event": "agent_start", "agent": "Matcher", "task": "TASK-02"}
        ...
        {"event": "report_ready", "path": "candidate_report.md", "size": 61239}
Step 7: Next.js API route reads stdout line-by-line, formats as SSE events
Step 8: Browser EventSource receives events, Zustand store updates
Step 9: assistant-ui components re-render with new data
Step 10: Agent Status Panel shows real-time progress
Step 11: On "report_ready" event, final report is displayed in chat
```

**Source**: integration-notes.md §3, SAD v1 §6.1

### 3.5 API Design

| Endpoint | Method | Purpose | Request Body | Response |
|----------|--------|---------|-------------|----------|
| `/api/chat` | POST | Start recruitment workflow | `{ job_requirements: { title, description, responsibilities, qualifications, ... } }` | SSE stream |
| `/api/chat/status` | GET | Check workflow status | — | `{ status: "running"|"complete"|"error", elapsed_seconds: 123 }` |
| `/api/chat/{id}/report` | GET | Retrieve completed report | — | `{ report: "# Markdown...", path: "..." }` |
| `/api/setup/check` | GET | Check if configured | — | `{ configured: true/false, missing_keys: ["OPENAI_API_KEY"] }` |
| `/api/setup/validate` | POST | Validate API key | `{ provider: "glm-5.2", api_key: "...", base_url: "..." }` | `{ valid: true/false, message: "..." }` |

**Source**: PRD §4.7, phase-3-outline.md §2

### 3.6 SSE Protocol Design

The SSE protocol carries structured JSON events from the Python subprocess to the browser:

```
event: agent_start
data: {"agent":"Researcher","task":"TASK-01","timestamp":"2026-07-08T10:00:00Z"}

event: agent_progress
data: {"agent":"Researcher","progress":45,"message":"Searching for Python developers on LinkedIn..."}

event: agent_complete
data: {"agent":"Researcher","output":"Found 12 candidates","duration_seconds":52,"timestamp":"2026-07-08T10:00:52Z"}

event: agent_start
data: {"agent":"Matcher","task":"TASK-02","timestamp":"2026-07-08T10:00:52Z"}

event: error
data: {"code":"TOOL_UNAVAILABLE","message":"SerperDevTool rate limit reached","severity":"warning"}

event: report_ready
data: {"report_path":"candidate_report.md","size_bytes":61239,"duration_total":541,"timestamp":"2026-07-08T10:09:01Z"}

event: workflow_complete
data: {"status":"success","candidates_found":10,"avg_score":87.3}
```

The Next.js API route translates the Python stdout JSON lines to proper SSE `event:` + `data:` lines for the browser's `EventSource` API.

### 3.7 Integration with Existing CLI Backend (Strangler Fig Pattern)

The CLI codebase from v0.1.0 remains **completely intact**. The web UI (v0.2.0) does NOT modify `main.py`, `crew.py`, or any Python code. Instead, it adds a **wrapper service** that calls the same `RecruitmentCrew` class via subprocess.

**Strangler Fig Pattern implementation:**

```
v0.1.0 Code (unchanged):
├── src/recruitment/main.py         ← CLI entry point (still works)
├── src/recruitment/crew.py         ← RecruitmentCrew class
├── src/recruitment/config/*.yaml   ← Agent/task configs
├── src/recruitment/tools/*.py      ← Tool implementations

v0.2.0 Additions (new files only):
├── nextjs-app/                     ← New Next.js application
│   ├── src/app/api/chat/route.ts   ← SSE streaming API route
│   ├── src/app/page.tsx            ← Chat UI page
│   ├── src/components/             ← React components
│   ├── package.json                ← Node dependencies
│   └── next.config.js              ← Next.js configuration
└── scripts/
    └── run_recruitment_sse.py      ← New: SSE-aware CLI wrapper
                                    ← (calls same RecruitmentCrew)
```

The CLI continues to work via `uv run recruitment`. The web UI works via `npm run dev` + `uv run recruitment --sse`. Both share the same Python CrewAI backend.

**Source**: SAD v1 §3.4 ("Strangler Fig pattern" is our documented approach), integration-notes.md §3

### 3.8 QA Issue Remediation in v0.2.0

| Issue | Fix | Location | Status |
|-------|-----|----------|--------|
| **QA-01**: Simulated progress spinner | SSE streaming from real CrewAI execution replaces `time.sleep(1)` mock | `main.py:373-379` → new SSE protocol | Fixed |
| **QA-02**: Missing `.env` file | Interactive web UI setup wizard with API key validation | New `/api/setup/*` endpoints | Fixed |
| **QA-03**: CrewAI deprecation warnings | Monitor CrewAI releases; suppress warnings via `warnings.filterwarnings()` in SSE wrapper | CrewAI internals | Mitigated |
| **QA-04**: Double `RecruitmentCrew` init | Single initialization via subprocess — web UI spawns one process; CLI refactored to lazy-init | `main.py:354,379` | Fixed |

**Source**: qa-plan.md §5.2, §5.3, §7.1, §7.2, technical-debt.md §1

---

## 4. v0.3.0 — ATS Integration Architecture

### 4.1 Integration Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                        CrewAI Agents                              │
│   (Workflow uses ATS data for research + reports back results)    │
└──────────────────────────┬─────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────────┐
│                     ATS Adapter Interface                          │
│  (Abstract base class defining integration contract)               │
│                                                                    │
│  Methods:                                                          │
│  - push_candidate_report(job_id, report_data) → bool              │
│  - pull_job_descriptions(filters) → List[JobDescription]          │
│  - authenticate(credentials) → bool                               │
│  - validate_connection() → ConnectionStatus                       │
│  - get_job_details(job_id) → JobDescription                       │
│  - add_candidate_note(job_id, candidate_id, note) → bool          │
└──────────┬──────────────────────────────────┬──────────────────────┘
           │                                  │
           ▼                                  ▼
┌──────────────────────┐       ┌──────────────────────┐
│  GreenhouseAdapter   │       │    LeverAdapter      │
│                      │       │                      │
│  - OAuth 2.0 flow    │       │  - OAuth 2.0 flow    │
│  - REST API v1       │       │  - REST API v1       │
│  - Token storage     │       │  - Token storage     │
│  - Rate limiting     │       │  - Rate limiting     │
└──────────┬───────────┘       └──────────┬───────────┘
           │                              │
           ▼                              ▼
┌──────────────────────┐       ┌──────────────────────┐
│   Greenhouse API     │       │     Lever API        │
│   (oauth.greenhouse. │       │   (api.lever.co)     │
│    io)               │       │                      │
└──────────────────────┘       └──────────────────────┘
```

**Source**: PRD §8.2 (v0.3.0), MRD §4 (competitive gaps), phase-3-outline.md §3

### 4.2 ATS Adapter Interface (Abstract Base Class)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class JobDescription:
    id: str
    title: str
    description: str
    requirements: list[str]
    responsibilities: list[str]
    location: str
    posted_date: str
    status: str  # "open", "closed", "draft"

@dataclass
class ConnectionStatus:
    connected: bool
    provider: str
    account_name: str
    rate_limit_remaining: int
    rate_limit_reset: int

class ATSAdapter(ABC):
    """Abstract interface for ATS platform integration."""

    @abstractmethod
    def authenticate(self, client_id: str, client_secret: str,
                     redirect_uri: str, auth_code: str) -> dict:
        """Perform OAuth 2.0 authorization code flow."""
        pass

    @abstractmethod
    def validate_connection(self) -> ConnectionStatus:
        """Verify the current connection is valid and return status."""
        pass

    @abstractmethod
    def pull_job_descriptions(self, status: str = "open",
                              limit: int = 50) -> list[JobDescription]:
        """Retrieve job descriptions from the ATS."""
        pass

    @abstractmethod
    def get_job_details(self, job_id: str) -> JobDescription:
        """Get detailed information for a specific job."""
        pass

    @abstractmethod
    def push_candidate_report(self, job_id: str,
                              report_data: dict) -> bool:
        """Attach or link a candidate report to a job in the ATS."""
        pass

    @abstractmethod
    def add_candidate_note(self, job_id: str, candidate_id: str,
                           note: str) -> bool:
        """Add a note about a candidate to the ATS record."""
        pass
```

### 4.3 OAuth 2.0 Flow

Both Greenhouse and Lever use the OAuth 2.0 Authorization Code flow:

```
┌─────────┐         ┌──────────┐         ┌───────────┐
│ Browser │         │ Next.js  │         │ ATS       │
│  (User) │         │ Backend  │         │ Provider  │
└────┬────┘         └────┬─────┘         └─────┬─────┘
     │                   │                     │
     │ 1. "Connect ATS"  │                     │
     │─── Click button ──→                     │
     │                   │                     │
     │ 2. Generate auth URL                    │
     │                   │                     │
     │ 3. Redirect to ATS login                │
     │←────────────────────────────────────────→│
     │                   │                     │
     │ 4. User authorizes                      │
     │←────────────────────────────────────────→│
     │                   │                     │
     │ 5. Auth code returned to callback URL   │
     │←────────────────────────────────────────→│
     │                   │                     │
     │ 6. POST /api/ats/callback               │
     │─── { code } ──────→                     │
     │                   │                     │
     │ 7. Exchange code for tokens             │
     │                   │── POST ────────────→│
     │                   │← { access,refresh }─│
     │                   │                     │
     │ 8. Encrypt & store tokens in DB         │
     │                   │                     │
     │ 9. Return "Connected!"                  │
     │←── { success } ────│                     │
     │                   │                     │
```

**Token Storage Strategy** (v0.5.0+ database):
- Access tokens: Encrypted at rest (AES-256) in `ats_credentials` table
- Refresh tokens: Same table, rotated on each refresh
- Token expiry: Stored; auto-refresh before API calls
- Multi-tenant: Tokens scoped to organization (v1.0.0)

### 4.4 Data Sync Strategy

**Inbound Sync (ATS → CrewAI):**

| Trigger | Action | Frequency |
|---------|--------|-----------|
| User selects "Import from ATS" | Pull open job descriptions from connected ATS | On-demand |
| Scheduled sync | Refresh job list from ATS | Daily (configurable) |
| Webhook (future) | ATS pushes new/updated jobs to webhook endpoint | Real-time |

**Outbound Sync (CrewAI → ATS):**

| Trigger | Action | Data Pushed |
|---------|--------|-------------|
| Report generated | Push candidate report URL/summary to ATS job record | Report link, candidate count, top scores |
| User action | Add candidate note to ATS record | Candidate name, score, recommendation |
| Batch export | Export all candidates from a workflow run | Structured JSON matching ATS import format |

**Source**: MRD §4.1 (competitive gaps — ATS integration is most requested feature), phase-3-outline.md §3

### 4.5 Adapter Registration Pattern

The ATS adapter system uses a registry pattern for extensibility:

```python
# ats/registry.py
class ATSRegistry:
    _adapters: dict[str, type[ATSAdapter]] = {}

    @classmethod
    def register(cls, name: str, adapter_class: type[ATSAdapter]):
        cls._adapters[name] = adapter_class

    @classmethod
    def get_adapter(cls, name: str, config: dict) -> ATSAdapter:
        if name not in cls._adapters:
            raise ValueError(f"Unknown ATS provider: {name}")
        return cls._adapters[name](config)

# ats/greenhouse.py
@ATSRegistry.register("greenhouse")
class GreenhouseAdapter(ATSAdapter): ...

# ats/lever.py
@ATSRegistry.register("lever")
class LeverAdapter(ATSAdapter): ...
```

Adding a new ATS in the future (e.g., Workday, BambooHR) requires only:
1. Create a new adapter class implementing `ATSAdapter`
2. Register it with the `@ATSRegistry.register("name")` decorator
3. No changes to agent code, API routes, or UI components

---

## 5. v0.4.0 — Multi-Role & Hierarchical Process

### 5.1 Architecture Change: Sequential → Hierarchical

MVP (v0.1.0) uses a **sequential process** where agents execute one after another:

```
Sequential (MVP):
[Researcher] → [Matcher] → [Communicator] → [Reporter]
    52s           48s           120s             30s       = 250s total (4m 10s)
```

Phase 3 v0.4.0 introduces a **hierarchical process** with a **Manager Agent** that delegates to specialized sub-agents and coordinates parallel execution:

```
Hierarchical (v0.4.0):
                      ┌─────────────────────────────┐
                      │     Manager Agent            │
                      │  (Role: Recruitment Manager)  │
                      │  (allow_delegation: true)     │
                      └──────────┬──────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
     ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
     │  Sub-Crew A    │ │  Sub-Crew B    │ │  Sub-Crew C    │
     │  (Job A)       │ │  (Job B)       │ │  (Job C)       │
     │  Sequential    │ │  Sequential    │ │  Sequential    │
     │   4 agents     │ │   4 agents     │ │   4 agents     │
     └────────┬───────┘ └────────┬───────┘ └────────┬───────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
                                 ▼
                      ┌─────────────────────────────┐
                      │     Result Aggregation       │
                      │  (Manager merges outputs)    │
                      │  → Combined report           │
                      └─────────────────────────────┘
```

**Source**: PRD §10 (Assumption 7 — hierarchical deferred), SAD v1 §1.2, phase-3-outline.md §4

### 5.2 Manager Agent Design

| Property | Value |
|----------|-------|
| **Role** | Recruitment Manager |
| **Goal** | Coordinate multi-agent team for efficient candidate processing across multiple job requirements |
| **Backstory** | You are an experienced recruitment manager who excels at delegating tasks, coordinating multiple hiring pipelines, and ensuring consistent quality across all candidate evaluations. |
| **Delegation** | Enabled (`allow_delegation: true`) |
| **Tools** | Task assignment, progress tracking, result aggregation |
| **Process Type** | `Process.hierarchical` |
| **Memory** | Enabled (tracks all sub-crew outputs) |
| **LLM Strategy** | More capable model recommended for Manager (e.g., GLM-5.2); sub-agents can use smaller/faster models |

**Manager Agent Responsibilities:**
1. **Job Assignment**: Receive multiple job descriptions, assign each to a dedicated sub-crew
2. **Parallel Orchestration**: Launch sub-crews in parallel where dependencies allow
3. **Progress Monitoring**: Track each sub-crew's progress, handle failures
4. **Result Aggregation**: Collect all sub-crew outputs, merge into a consolidated report
5. **Quality Assessment**: Compare candidate quality across jobs for resource allocation
6. **Error Recovery**: Retry failed sub-crews or redistribute work

### 5.3 Multi-Role Support Architecture

The input model is extended to accept multiple job descriptions simultaneously:

```json
{
  "jobs": [
    {
      "id": "job-001",
      "title": "Senior Python Developer",
      "description": "...",
      "responsibilities": ["...", "..."],
      "qualifications": ["...", "..."]
    },
    {
      "id": "job-002",
      "title": "Frontend Engineer",
      "description": "...",
      "responsibilities": ["...", "..."],
      "qualifications": ["...", "..."]
    }
  ],
  "cross_candidate_sharing": true,
  "output_format": "combined"
}
```

Key architectural changes:
- **Input schema** grows from single JD to array of JDs
- **`RecruitmentCrew`** detects multi-JD input and switches to hierarchical process
- **Single-JD inputs** continue to use the original sequential process (backward compatible)
- **`Manager Agent`** dynamically creates sub-crews per job
- **Output** is either a combined report (all jobs) or per-job reports

### 5.4 Parallel Execution Strategy

```
Timeline comparison (3 job descriptions):

Sequential (v0.1.0 - extended for 3 jobs):
Job-A: [R][M][C][Rep]                                          = 250s
Job-B:                           [R][M][C][Rep]                 = 250s
Job-C:                                          [R][M][C][Rep]  = 250s
Total: 750s (12.5 min)

Hierarchical + Parallel (v0.4.0):
Manager: [Setup]                      [A]
Job-A:         [R][M][C][Rep]          |
Job-B:         [R][M][C][Rep]          +--[Aggregate] Total: ~280s
Job-C:         [R][M][C][Rep]          |
Total: ~280s (4.7 min) — well within the 5-min target (PRD §5.1)
```

**Parallelism Rules:**
- Independent job descriptions → execute in parallel (separate sub-crews)
- Dependent tasks within a job → remain sequential (Researcher → Matcher → Communicator → Reporter)
- Cross-job candidate matching → optional post-processing step after all sub-crews complete
- Manager agent overhead → minimal (~30s for setup + aggregation)

### 5.5 Performance Impact on Known Issues

The hierarchical process directly addresses the **E2E execution time gap** documented in technical-debt.md §3:

| Metric | Target (PRD §5.1) | v0.1.0 Actual | v0.4.0 Target |
|--------|-------------------|---------------|---------------|
| E2E single JD | < 5 min | 9m 1s (541s) | < 4 min |
| E2E three JDs | < 5 min (per JD) | N/A (sequential) | < 5 min total |
| Agent task time | < 90s per task | 48-120s | < 90s |

**Performance optimizations in v0.4.0:**
1. Parallel sub-crew execution (3x throughput improvement for multi-JD)
2. Manager Agent optimizes LLM usage by delegating context-specific tasks
3. Reduced context window pressure per agent (sub-crews have narrower focus)
4. Caching shared between sub-crews (same Serper.dev results reused)

**Source**: technical-debt.md §3, PRD §5.1 (NFR-001)

### 5.6 Backward Compatibility

The hierarchical process is **opt-in**. Existing code paths remain unchanged:

```python
# crew.py — v0.4.0 detection logic
class RecruitmentCrew:
    def kickoff(self, job_requirements, jobs: list = None):
        if jobs and len(jobs) > 1:
            # New: hierarchical process with Manager Agent
            return self._kickoff_hierarchical(jobs)
        else:
            # Existing: sequential process (v0.1.0 compatible)
            return self._kickoff_sequential(job_requirements)
```

The CLI continues to use the sequential path. The web UI (v0.2.0) enables multi-JD input when v0.4.0 is deployed.

---

## 6. v0.5.0 — Analytics & Database

### 6.1 Database Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     SQLAlchemy ORM                            │
│  (Declarative Base + Alembic Migrations)                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                  SQLite Database                        │    │
│  │         (production: PostgreSQL via same ORM)           │    │
│  │                                                         │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │    │
│  │  │ workflow_   │  │ candidates   │  │ scores       │  │    │
│  │  │ runs        │  │              │  │              │  │    │
│  │  ├─────────────┤  ├──────────────┤  ├──────────────┤  │    │
│  │  │ id (PK)     │  │ id (PK)      │  │ id (PK)      │  │    │
│  │  │ status      │  │ workflow_id  │  │ candidate_id │  │    │
│  │  │ start_time  │  │ name         │  │ dimension    │  │    │
│  │  │ end_time    │  │ role         │  │ score        │  │    │
│  │  │ duration_s  │  │ location     │  │ weight       │  │    │
│  │  │ llm_provider│  │ skills       │  │ justification│  │    │
│  │  │ llm_model   │  │ profile_url  │  │              │  │    │
│  │  │ input_jobs  │  │ source       │  │              │  │    │
│  │  │ agents_used │  │ overall_score│  │              │  │    │
│  │  │ report_path │  │ confidence   │  │              │  │    │
│  │  │ created_at  │  │ rank         │  │              │  │    │
│  └──────┼─────────┘  │ matched_job  │  │              │  │    │
│         │            └──────┼───────┘  └──────┼───────┘  │    │
│         │                   │                  │          │    │
│         ▼                   ▼                  ▼          │    │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │    │
│  │ agents      │  │ tasks        │  │ reports      │      │    │
│  ├─────────────┤  ├──────────────┤  ├──────────────┤      │    │
│  │ id (PK)     │  │ id (PK)      │  │ id (PK)      │      │    │
│  │ workflow_id │  │ workflow_id  │  │ workflow_id  │      │    │
│  │ agent_name  │  │ task_name    │  │ format       │      │    │
│  │ agent_role  │  │ start_time   │  │ content      │      │    │
│  │ start_time  │  │ end_time     │  │ file_path    │      │    │
│  │ end_time    │  │ duration_s   │  │ size_bytes   │      │    │
│  │ status      │  │ status       │  │ created_at   │      │    │
│  │ output_summary   │ input_summary   │              │      │    │
│  └─────────────┘  └──────────────┘  └──────────────┘      │    │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐                           │    │
│  │ outreach_   │  │ ats_         │  (v0.3.0 addition)        │    │
│  │ templates   │  │ credentials  │                           │    │
│  ├─────────────┤  ├──────────────┤                           │    │
│  │ id (PK)     │  │ id (PK)      │                           │    │
│  │ workflow_id │  │ organization_id (v1.0.0 tenant)          │    │
│  │ candidate_id│  │ provider     │                           │    │
│  │ channel     │  │ access_token (encrypted)                 │    │
│  │ subject     │  │ refresh_token (encrypted)                │    │
│  │ body        │  │ expires_at   │                           │    │
│  │ sequence    │  │ created_at   │                           │    │
│  │ created_at  │  │ updated_at   │                           │    │
│  └─────────────┘  └──────────────┘                           │    │
└──────────────────────────────────────────────────────────────┘
```

**Source**: PRD §8.2 (v0.5.0), SAD v1 §4.3 (database reference), phase-3-outline.md §5

### 6.2 Entity Relationship Summary

| Entity | Key Relationships | Purpose |
|--------|-------------------|---------|
| `workflow_runs` | → agents, tasks, candidates, reports | Each execution of the recruitment workflow |
| `agents` | → workflow_runs | Per-workflow agent execution records |
| `tasks` | → workflow_runs | Per-workflow task execution records |
| `candidates` | → workflow_runs, scores, outreach_templates | Candidate profiles discovered during workflow |
| `scores` | → candidates | Multi-dimensional scoring breakdown per candidate |
| `reports` | → workflow_runs | Generated report content and metadata |
| `outreach_templates` | → workflow_runs, candidates | Generated outreach content |
| `ats_credentials` | → organization (v1.0.0) | Encrypted OAuth tokens for ATS connections |

### 6.3 Analytics Dashboard

The analytics dashboard uses the existing Next.js frontend (v0.2.0) and queries the SQLite database (via the same database file accessible to the Next.js server). The dashboard is a new route at `/dashboard`:

**Dashboard Components:**

| Component | Data Source | Description |
|-----------|-------------|-------------|
| **Time-to-Fill Trend** | `workflow_runs` | Line chart of E2E execution times over last N runs |
| **Candidate Pipeline** | `candidates` + `scores` | Funnel: sourced → scored → outreached → (future) contacted |
| **Agent Performance** | `agents` + `tasks` | Average completion time per agent, success rate |
| **LLM Usage** | `workflow_runs` | Provider breakdown, total cost estimate, token count |
| **Execution History** | `workflow_runs` | Searchable table of past runs with status, duration, jobs |
| **Top Candidates** | `candidates` + `scores` | Best-scoring candidates across all recent workflows |
| **Export** | All tables | Export analytics data as CSV for external analysis |

**Implementation approach:**
- Next.js Server Components fetch data directly from SQLite (via a shared database module)
- Charts rendered with Recharts (lightweight, React-native charting)
- Dashboard is read-only; no write operations from the dashboard
- Data refresh: On page load + manual refresh button

### 6.4 Migration Strategy (SQLite → PostgreSQL)

The ORM abstraction (SQLAlchemy) enables migration without application code changes:

| Phase | Database | When | Migration Method |
|-------|----------|------|-----------------|
| v0.5.0 MVP | SQLite | Initial analytics release | File-based, zero config |
| v0.5.x | SQLite | Scaling to single-team | Same as above |
| v1.0.0 pre-prod | PostgreSQL | Before multi-tenant launch | Alembic migration script |
| v1.0.0 prod | PostgreSQL (managed) | Production deployment | Managed DB service (RDS, Cloud SQL) |

**Migration script overview:**
```python
# alembic/versions/xxx_migrate_to_postgres.py
def upgrade():
    # Create all tables in PostgreSQL (mirroring SQLite schema)
    # Migrate data: read from SQLite, write to PostgreSQL
    # Update connection string in application config
    pass
```

**Source**: SAD v1 §4.3 (database reference — "SQLite for conversation history and analytics")

---

## 7. v1.0.0 — Production Architecture

### 7.1 Authentication & Multi-Tenancy

```
┌────────────────────────────────────────────────────────────────────┐
│                         Clerk / Auth0                              │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  Organization: Acme Corp (tenant_id: org_abc123)            │   │
│  │  ├── User: alice@acme.com (role: admin)                    │   │
│  │  ├── User: bob@acme.com (role: recruiter)                  │   │
│  │  └── User: carol@acme.com (role: viewer)                   │   │
│  │                                                             │   │
│  │  Organization: Beta Inc (tenant_id: org_def456)             │   │
│  │  ├── User: dave@beta.com (role: admin)                     │   │
│  │  └── User: eve@beta.com (role: recruiter)                  │   │
│  └────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│                    Next.js Middleware                               │
│  - Protects all routes except /, /about, /pricing                  │
│  - Redirects unauthenticated users to Clerk-hosted login           │
│  - Attaches tenant_id to request context                           │
│  - Enforces RBAC on /admin and /settings routes                    │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│                    Multi-Tenant Data Isolation                      │
│                                                                   │
│  All database queries scoped by tenant_id:                         │
│  - workflow_runs WHERE organization_id = :tenant_id               │
│  - candidates JOIN workflow_runs ON org_id                        │
│  - ats_credentials WHERE organization_id = :tenant_id             │
│  - Reports stored in tenant-scoped paths (/data/tenant_id/)       │
└────────────────────────────────────────────────────────────────────┘
```

**Source**: PRD §8.2 (v1.0.0), PRD §2.1 (Assumption 3), phase-3-outline.md §6

### 7.2 Role-Based Access Control (RBAC)

| Role | Permissions | Routes |
|------|-------------|--------|
| **Admin** | Full access: configure, execute, view all, manage team, manage ATS connections | All routes |
| **Recruiter** | Execute workflows, view own runs, view shared reports | `/chat`, `/dashboard`, `/reports` |
| **Viewer** | View reports and dashboard only | `/dashboard`, `/reports/*` (read-only) |

### 7.3 Deployment Architecture

```
                          ┌─────────────┐
                          │  Cloud Load │
                          │  Balancer   │
                          └──────┬──────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │  Next.js  │ │  Next.js │ │  Next.js │
              │  Pod v1   │ │  Pod v2  │ │  Pod v3  │
              │  :3000    │ │  :3000   │ │  :3000   │
              └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
                    │             │             │
                    └─────────────┼─────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │CrewAI    │ │CrewAI    │ │CrewAI    │
              │Worker v1 │ │Worker v2 │ │Worker v3 │
              │(Python)  │ │(Python)  │ │(Python)  │
              └──────────┘ └──────────┘ └──────────┘
                    │             │             │
                    └─────────────┼─────────────┘
                                  │
                                  ▼
                          ┌──────────────┐
                          │  PostgreSQL  │
                          │  (Managed)   │
                          └──────────────┘
```

#### Docker Multi-Stage Build

```dockerfile
# Stage 1: Python base
FROM python:3.12-slim AS python-base
WORKDIR /app
RUN pip install uv
COPY pyproject.toml .
RUN uv sync --no-dev

# Stage 2: Node base
FROM node:20-alpine AS node-base
WORKDIR /app
COPY nextjs-app/package.json nextjs-app/ .
RUN npm ci --only=production

# Stage 3: Production
FROM python:3.12-slim
WORKDIR /app
COPY --from=python-base /app /app
COPY --from=node-base /app/.next /app/.next
COPY src/ /app/src/
COPY nextjs-app/ /app/nextjs-app/
EXPOSE 3000
CMD ["node", "nextjs-app/server.js"]
```

#### Kubernetes Manifests

| Resource | Purpose |
|----------|---------|
| `Deployment` | 3 replicas of Next.js + Python sidecar |
| `Service` | Load-balanced internal service on port 3000 |
| `Ingress` | HTTPS termination, routing rules |
| `ConfigMap` | Non-sensitive config (LLM_MODEL, log levels) |
| `Secret` | API keys, database credentials, JWT secrets |
| `HorizontalPodAutoscaler` | Scale based on CPU/memory utilization |
| `NetworkPolicy` | Pod-to-pod communication restrictions |

### 7.4 Security & Compliance

| Concern | Implementation | Phase |
|---------|---------------|-------|
| **GDPR** | Data processing agreement, right to erasure API, data minimization | v1.0.0 |
| **EEOC** | Bias monitoring in scoring dimension analysis, fairness audit trail | v1.0.0 |
| **SOC 2** | Audit logging, access controls, encryption at rest | v1.0.0+ |
| **Data Encryption** | AES-256 at rest for credentials, TLS 1.3 in transit | v1.0.0 |
| **API Rate Limiting** | Token bucket per user per route (100 req/min standard) | v0.2.0+ |
| **Secrets Management** | Kubernetes Secrets → environment variables (never in code) | v1.0.0 |
| **Environment Isolation** | Dev, staging, prod with separate databases and credentials | v1.0.0 |

**Source**: PRD §5.3 (NFR-003), PRD §2.1 (Assumption 3 — multi-tenancy deferred), MRD §9 (risks)

---

## 8. Cross-Cutting Architecture Decisions

### 8.1 API Layer Design (All Versions)

The API layer evolves across versions, growing from zero (v0.1.0 CLI-only) to a full three-tier architecture (v1.0.0):

```
v0.1.0: No API layer — direct Python CLI
v0.2.0: Next.js API Routes (BFF) + Python subprocess
v0.5.0: Next.js API Routes + Database queries
v1.0.0: Next.js API Routes + Auth middleware + Worker pool
```

**Three-tier API architecture at v1.0.0:**

| Tier | Technology | Responsibility | Scale Unit |
|------|-----------|----------------|------------|
| **Tier 1: BFF** | Next.js API Routes | Auth, routing, SSE streaming, validation, caching | Horizontal (K8s pods) |
| **Tier 2: CrewAI Service** | Python + CrewAI | Agent orchestration, LLM calls, tool execution | Worker pool |
| **Tier 3: External** | ATS APIs, LLM APIs, Serper.dev | Data sourcing, AI inference, integrations | External |

**Key design rules:**
- Next.js never imports Python modules directly (subprocess boundary)
- Python service never handles HTTP directly (Next.js is the sole HTTP entry point)
- Database access is through Next.js API routes (read/write) and Python (write only for workflow results)
- No direct database access from the browser

### 8.2 LLM Provider Configuration

Updated from MVP to support provider switching via web UI:

```python
# crew.py — v0.2.0+ LLM configuration
import os
from crewai import LLM

def create_llm():
    provider = os.getenv("LLM_PROVIDER", "openai")  # "openai", "ollama", "custom"
    model = os.getenv("LLM_MODEL", "glm-5.2")
    base_url = os.getenv("LLM_BASE_URL", "https://api.iamhc.cn/v1")
    api_key = os.getenv("OPENAI_API_KEY", "")

    if provider == "ollama":
        return LLM(model="ollama/llama3", base_url="http://localhost:11434")
    elif provider == "custom":
        return LLM(model=model, base_url=base_url, api_key=api_key)
    else:
        return LLM(model=model, base_url=base_url, api_key=api_key)
```

**v0.2.0 web UI enhancement:** The setup wizard (fixing QA-02) provides a dropdown UI for LLM provider selection, model name input, and test-connection button.

**Source**: PRD §4.8 (FR-008), SAD v1 §4.4, technical-debt.md §5

### 8.3 CI/CD Pipeline

| Version | CI/CD Status | Tools |
|---------|-------------|-------|
| v0.1.0 | None (local only) | — |
| v0.2.0 | GitHub Actions: lint + type-check + test | `ruff`, `mypy`, `pytest`, `npm test` |
| v0.3.0 | + Integration tests with mocked ATS | `pytest`, `responses` (HTTP mock) |
| v0.4.0 | + Performance benchmarks | `pytest-benchmark` |
| v0.5.0 | + Docker build + push to registry | `docker buildx`, `docker push` |
| v1.0.0 | + Deploy to Kubernetes (staging) | `kubectl`, `helm` |

**GitHub Actions workflow (v0.2.0+):**
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - uses: astral-sh/setup-uv@v3
      - run: uv sync
      - run: uv run ruff check .
      - run: uv run mypy src/
      - run: uv run pytest tests/ -v --cov=recruitment
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: npm ci
        working-directory: nextjs-app
      - run: npm run lint
        working-directory: nextjs-app
      - run: npm run test
        working-directory: nextjs-app
```

**Source**: phase-3-outline.md §7, technical-debt.md §4 (testing debt)

### 8.4 Monitoring & Observability

| Layer | Tool / Method | Metrics |
|-------|--------------|---------|
| **Application Logs** | Structured JSON (stdout) → ELK / Loki | Agent events, task duration, errors |
| **Python Metrics** | `structlog` for agent execution logs | Per-agent time, LLM latency, tool errors |
| **Next.js Metrics** | OpenTelemetry (OTEL) + instrumentation | Request duration, SSE event count, error rate |
| **Infrastructure** | Kubernetes monitoring (Prometheus + Grafana) | Pod CPU/memory, request rate, P99 latency |
| **Business Metrics** | Analytics dashboard (v0.5.0) | Workflow completion rate, avg E2E time, candidate yield |

**Alerting Rules (v1.0.0):**
- Workflow failure rate > 5% in 5-minute window
- E2E execution time > 10 minutes
- LLM API error rate > 10%
- ATS connection failures > 3 in 1 hour
- Disk usage > 80% (report storage)

---

## 9. Technical Debt Remediation

All known issues from MVP (technical-debt.md §1, qa-plan.md §5.2-5.3) are mapped to Phase 3 versions:

| Issue | Version Fixed | Fix Strategy | Source |
|-------|--------------|--------------|--------|
| **QA-01**: Simulated progress | v0.2.0 / v0.2.1 | SSE streaming from real CrewAI execution replaces `time.sleep(1)` mock | qa-plan.md §7.1, technical-debt.md §1 |
| **QA-02**: Missing .env file | v0.2.0 / v0.2.1 | Interactive web UI setup wizard + auto-env generation | qa-plan.md §7.1, technical-debt.md §1 |
| **QA-03**: Deprecation warnings | v0.2.0+ (ongoing) | Monitor CrewAI releases; suppress via `warnings.filterwarnings()` in SSE wrapper | qa-plan.md §7.2, technical-debt.md §1 |
| **QA-04**: Double init | v0.2.1 | Refactor `RecruitmentCrew` lifecycle: lazy initialization with singleton pattern | qa-plan.md §7.2, technical-debt.md §1 |
| **E2E time > 5 min** | v0.4.0 | Hierarchical process with parallel sub-crews; LLM response caching | technical-debt.md §3 |
| **No ruff/mypy in CI** | v0.2.0 | GitHub Actions workflow with ruff check + mypy | technical-debt.md §4 |
| **No coverage reporting** | v0.2.0 | pytest-cov in CI pipeline | technical-debt.md §4 |
| **No mocked-LLM E2E test** | v0.2.0 | Add E2E test with mocked `crew.kickoff()` | technical-debt.md §4 |
| **LLM config docs gap** | v0.2.0 | Updated .env.example comments + web UI setup wizard | technical-debt.md §5 |

**Source**: qa-plan.md §5, §7, technical-debt.md §1-§5

---

## 10. Architecture Validation Checklist

- [x] v0.2.0 architecture supports SSE streaming from Python CrewAI backend via subprocess
- [x] v0.2.0 Strangler Fig pattern preserves CLI while adding web UI
- [x] v0.2.0 QA-01, QA-02, QA-04 fixes are explicitly designed
- [x] v0.3.0 ATS adapter interface is provider-agnostic (Greenhouse + Lever)
- [x] v0.3.0 OAuth 2.0 flow handles token storage and refresh
- [x] v0.4.0 hierarchical process reduces E2E time below 5 min target
- [x] v0.4.0 backward compatible with single-JD sequential execution
- [x] v0.5.0 database schema supports all analytics queries (7 entity types)
- [x] v0.5.0 ORM abstraction enables SQLite → PostgreSQL migration
- [x] v1.0.0 auth/multi-tenancy isolates tenant data at database level
- [x] v1.0.0 Docker + Kubernetes deployment architecture defined
- [x] v1.0.0 security & compliance controls defined (GDPR, EEOC, RBAC)
- [x] CI/CD pipeline evolves incrementally across versions
- [x] All 4 QA issues (QA-01 through QA-04) mapped to fix versions
- [x] Each version builds on prior without breaking changes

---

## 11. Assumptions

1. **Existing CLI (v0.1.0) remains functional** as Phase 3 features are added. The Strangler Fig pattern ensures no breaking changes to the Python codebase. (Source: SAD v1 §3.4)

2. **Web UI communicates via subprocess/SSE** (not HTTP API). The Next.js API route spawns `uv run recruitment --sse` and communicates over a SSE connection. This avoids building a separate HTTP server for the Python backend. (Source: Phase 3 architecture decision)

3. **Greenhouse/Lever APIs are available** for integration (v0.3.0). ATS platforms provide REST APIs with OAuth 2.0 authentication. API documentation is current and accessible. (Source: MRD §4, phase-3-outline.md §3)

4. **Hierarchical process with Manager Agent reduces E2E time** below the 5-minute PRD target. Parallel sub-crew execution for multiple job descriptions provides the primary speedup. (Source: PRD §5.1 NFR-001, technical-debt.md §3)

5. **SQLite is sufficient for initial analytics** (v0.5.0); PostgreSQL migration planned for v1.0.0. The ORM abstraction ensures zero application code changes during migration. (Source: SAD v1 §4.3)

6. **Clerk/Auth0 handles auth complexity**, keeping the backend auth-light. The Next.js middleware validates tokens and attaches tenant context. The Python service trusts the tenant ID forwarded by Next.js. (Source: phase-3-outline.md §6)

7. **API keys for LLM and Serper.dev** remain required in all versions. The web UI setup wizard (v0.2.0) makes configuration easier but does not eliminate the dependency. (Source: PRD §4.8)

8. **Single LLM provider per workflow execution** is sufficient. Provider switching happens between runs, not within a single run. The Manager Agent (v0.4.0) may use a different model than sub-agents. (Source: PRD §4.8, FR-008)

9. **Report output remains markdown-based** across all versions. The web UI renders markdown with syntax highlighting. PDF/HTML export is a future enhancement. (Source: PRD §4.6)

10. **No real-time candidate outreach** is performed by the system. The Communicator agent generates templates only; human recruiters send messages. This design constraint is maintained across all versions. (Source: PRD §1.3, Principle 3)

---

## 12. Open Questions for Phase 3

| # | Question | Impact | Suggested Resolution |
|---|----------|--------|---------------------|
| 1 | **SSE vs. WebSocket**: Should v0.2.0 use SSE or WebSocket for real-time streaming? SSE is simpler (HTTP-native), WebSocket enables bidirectional communication. | Streaming UX | SSE recommended for v0.2.0 (unidirectional enough); WebSocket for v0.4.0+ if agent feedback loops are needed |
| 2 | **Database concurrency**: SQLite has limited write concurrency. Should v0.5.0 start with PostgreSQL for multi-user scenarios? | Data integrity | Start with SQLite (WAL mode for read concurrency); PostgreSQL only when multi-tenant (v1.0.0) |
| 3 | **Manager Agent LLM cost**: The Manager Agent needs a capable LLM for delegation decisions. Should we recommend a specific model tier? | Cost vs. quality | Use same LLM as sub-agents; document upgrade path if Manager becomes bottleneck |
| 4 | **ATS webhook support**: Should v0.3.0 include webhook endpoints for ATS push-based sync? | Integration completeness | Defer to v0.3.x; v0.3.0 focuses on pull-based sync and OAuth |
| 5 | **Report format extensibility**: Should v1.0.0 support PDF, HTML, or JSON report export? | User flexibility | Defer; markdown is sufficient for v1.0.0 core use case |
| 6 | **Enterprise SSO**: Should v1.0.0 include SAML/OIDC SSO beyond Clerk basic auth? | Enterprise adoption | Clerk supports SAML/OIDC in enterprise plan; configure, don't build custom |

---

## Audit

| Field | Value |
|-------|-------|
| **AAMAD_TARGET_RUNTIME** | crewai |
| **Source Artifacts** | sad.md (v1.0), phase-3-outline.md, prd.md, mrd.md, architecture-plan.md, qa-plan.md, integration-notes.md, technical-debt.md, frontend-plan.md |
| **PRD Sections Referenced** | §1, §2, §4, §5, §6, §7, §8, §9, §10, §12, §13 |
| **MRD Sections Referenced** | §4, §5, §9 |
| **SAD v1 Sections Referenced** | §1, §2, §3, §4, §5, §6, §7, §10 |
| **QA Plan Sections Referenced** | §5, §7, §8 |
| **Phase 3 Outline Sections Referenced** | §1, §2, §3, §4, §5, §6, §7 |
| **Technical Debt Sections Referenced** | §1, §2, §3, §4, §5 |
| **Version** | v2.0 |
| **Assumptions Recorded** | 10 |
| **Open Questions Recorded** | 6 |
| **QA Issues Mapped to Fix Versions** | 4 (QA-01 through QA-04) |

---

*This SAD v2 defines the Phase 3 post-MVP architecture for the Recruitment Assistant application. It builds upon the v0.1.0 MVP foundation (documented in SAD v1) and evolves the architecture through five version increments to achieve production readiness at v1.0.0. Implementation begins with v0.2.0 (Web Chat UI) as the immediate next step.*
