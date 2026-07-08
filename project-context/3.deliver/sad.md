# System Architecture Document (SAD)

## Recruitment Assistant Application — CrewAI Multi-Agent System

**Document Version:** 1.0  
**Date:** July 7, 2026  
**Prepared by:** @system.arch (AAMAD Phase 2 — Build)  
**Input Sources:** project-context/1.define/prd.md, project-context/1.define/mrd.md  
**AAMAD_TARGET_RUNTIME:** crewai

---

## 1. MVP Architecture Philosophy & Principles

### 1.1 MVP Design Principles

The following principles guide every architectural decision in this MVP. They are derived from the PRD product principles (PRD §1.3) and tailored for the 2-week sprint constraint.

1. **Customer Feedback First**: The architecture must enable rapid iteration based on recruiter feedback. The CLI-first approach (PRD §2.1) allows deploying the core workflow immediately without UI development overhead. All agent outputs are structured and auditable, enabling recruiters to evaluate quality from day one.

2. **Modern LLM Interface**: The system leverages CrewAI's proven agent orchestration (MRD §5) with GLM-5.2 as the default LLM (via OpenAI-compatible endpoint), while supporting local LLM alternatives (Ollama, LM Studio) for privacy-sensitive deployments (PRD §1.3, Principle 5). The architecture is LLM-agnostic through LiteLLM compatibility.

3. **Automated Deployment**: The CLI application is self-contained Python requiring only `uv` for dependency management. No containerization or cloud infrastructure is needed for MVP. The architecture avoids unnecessary operational complexity.

4. **Observable by Default**: Every agent reasoning trace is logged (PRD §5.3, NFR-003). Verbose logging is enabled by default. Task outputs are structured for auditability. This satisfies the "Transparency Over Speed" principle (PRD §1.3, Principle 2).

### 1.2 Core vs. Future Features Decision Framework

| Category        | MVP (Phase 2)              | Deferred (Phase 3+)                     |
| --------------- | -------------------------- | --------------------------------------- |
| Agent Workflow  | 4-agent sequential process | Hierarchical process with manager agent |
| User Interface  | CLI input/output           | Web chat UI (Next.js + assistant-ui)    |
| Data Storage    | File-based report output   | SQLite conversation history             |
| Authentication  | None (single-user)         | Multi-tenancy, user auth                |
| ATS Integration | None                       | Greenhouse, Lever, Workday              |
| Analytics       | None                       | Dashboard, metrics tracking             |
| Deployment      | Local execution            | Docker, cloud deployment                |
| Testing         | Unit + integration tests   | Performance benchmarks, load testing    |

**Decision Rationale**: The PRD explicitly scopes the MVP as "CLI-first" (PRD §2.1, Assumption 2). The web chat UI is allocated 5 days of effort (PRD §7.3, F-023) but is designated as post-MVP (PRD §8.2, v0.2.0). This SAD focuses exclusively on the CLI workflow.

### 1.3 Technical Architecture Decisions

**Decision 1: Python CLI as Primary Interface**

- **Rationale**: CrewAI is a Python framework (PRD §6.2). A Python CLI eliminates the need for API route abstraction, frontend build tooling, and cross-language communication. The user interacts directly with the CrewAI runtime.
- **Trade-off**: No real-time streaming to a web UI. Progress is displayed via terminal output.
- **Source**: PRD §4.7 (FR-007), PRD §7.3 (F-020)

**Decision 2: CrewAI Sequential Process**

- **Rationale**: The reference architecture (MRD §5.2) uses a sequential process (TASK-01 → TASK-02 → TASK-03 → TASK-04). This is simpler to debug, easier to reason about, and sufficient for single-requisition workflows.
- **Trade-off**: No parallelism between agents. Total execution time is the sum of all task times.
- **Source**: PRD §4.1 (FR-001), PRD §10 (Assumption 7)

**Decision 3: File-Based Output**

- **Rationale**: The final report is saved as `candidate_report.md` (PRD §4.6). No database is needed for MVP. Configuration is YAML-based (PRD §4.8). Environment variables are managed via `.env`.
- **Trade-off**: No conversation history, no multi-session support, no analytics.
- **Source**: PRD §6.3 (Project Structure)

**Decision 4: GLM-5.2 as Default LLM (OpenAI-Compatible)**

- **Rationale**: The project uses GLM-5.2 via an OpenAI-compatible API endpoint (https://api.iamhc.cn) as the default LLM. This provides strong reasoning for candidate evaluation at competitive cost. Local LLM support via Ollama is available as an alternative (PRD §4.8, US-07). LiteLLM compatibility is preserved for provider switching.
- **Trade-off**: API costs per execution. Users without access to the GLM-5.2 endpoint must configure an alternative LLM provider.
- **Source**: PRD §6.2, PRD §10 (Assumption 4)

**Decision 5: SerperDevTool for Web Search**

- **Rationale**: The CrewAI example uses SerperDevTool for web search (MRD §5.1). It provides Google search results via API without requiring browser automation. Free tier is available for development.
- **Trade-off**: API costs for high-volume searches. Limited to search results, not full LinkedIn profiles.
- **Source**: PRD §4.3 (FR-003), PRD §9.1

---

## 2. Multi-Agent System Specification

### 2.1 Agent Architecture Requirements

The system comprises 4 specialized agents executing a sequential workflow (PRD §4.1). Each agent is defined in `config/agents.yaml` with role, goal, and backstory.

#### AGENT-01: Job Candidate Researcher

| Property   | Value                                                      | Source             |
| ---------- | ---------------------------------------------------------- | ------------------ |
| Role       | Job Candidate Researcher                                   | PRD §4.1           |
| Goal       | Find potential candidates for the job via web search       | PRD §4.1           |
| Tools      | SerperDevTool, ScrapeWebsiteTool                           | PRD §4.1, MRD §5.1 |
| Delegation | Disabled (`allow_delegation: false`)                       | PRD §4.1           |
| Backstory  | Adept at finding right candidates through online resources | PRD §6.4           |

**Responsibilities:**

- Search web sources for candidates matching job requirements (PRD §4.3)
- Collect: name, current role, location, skills summary, profile URL (PRD §4.3)
- Target minimum 10 candidates per search (PRD §4.3)
- Ensure no duplicate candidates (PRD §4.3)
- Verify source URLs are valid and accessible (PRD §4.3)

#### AGENT-02: Candidate Matcher and Scorer

| Property   | Value                                                   | Source             |
| ---------- | ------------------------------------------------------- | ------------------ |
| Role       | Candidate Matcher and Scorer                            | PRD §4.1           |
| Goal       | Score and rank candidates against job requirements      | PRD §4.1           |
| Tools      | SerperDevTool, ScrapeWebsiteTool                        | PRD §4.1, MRD §5.1 |
| Delegation | Disabled                                                | PRD §4.1           |
| Backstory  | Knack for matching candidates using advanced algorithms | PRD §6.4           |

**Responsibilities:**

- Evaluate each candidate against scoring dimensions (PRD §4.4):
  - Skills Match (40%): Required skills present in profile
  - Experience Level (25%): Years and relevance of experience
  - Education (15%): Degree and field of study
  - Location (10%): Geographic match to job location
  - Additional Factors (10%): Certifications, publications, awards
- Produce overall score 0-100 with dimension breakdown (PRD §4.4)
- Assign confidence level (high/medium/low) (PRD §4.4)
- Rank candidates from highest to lowest score (PRD §4.4)

#### AGENT-03: Candidate Outreach Strategist

| Property   | Value                                             | Source             |
| ---------- | ------------------------------------------------- | ------------------ |
| Role       | Candidate Outreach Strategist                     | PRD §4.1           |
| Goal       | Develop engagement strategies and templates       | PRD §4.1           |
| Tools      | SerperDevTool, ScrapeWebsiteTool                  | PRD §4.1, MRD §5.1 |
| Delegation | Disabled                                          | PRD §4.1           |
| Backstory  | Skilled at creating effective outreach strategies | PRD §6.4           |

**Responsibilities:**

- Create initial contact email/message template (PRD §4.5)
- Develop follow-up sequence (2-3 messages) (PRD §4.5)
- Generate interview invitation template (PRD §4.5)
- Provide personalization tokens per candidate (PRD §4.5)
- Recommend outreach channel (email, LinkedIn, etc.) (PRD §4.5)
- Ensure professional tone aligned with employer brand (PRD §4.5)

#### AGENT-04: Candidate Reporting Specialist

| Property   | Value                                                   | Source             |
| ---------- | ------------------------------------------------------- | ------------------ |
| Role       | Candidate Reporting Specialist                          | PRD §4.1           |
| Goal       | Compile recruiter-ready final report                    | PRD §4.1           |
| Tools      | None (synthesis only)                                   | PRD §4.1, MRD §5.1 |
| Delegation | Disabled                                                | PRD §4.1           |
| Backstory  | Proficient at compiling detailed reports for recruiters | PRD §6.4           |

**Responsibilities:**

- Compile all previous task outputs into final report (PRD §4.6)
- Format report as markdown (PRD §4.6)
- Include agent reasoning traces for auditability (PRD §4.6)
- Save report to `candidate_report.md` (PRD §4.6)

### 2.2 Agent Collaboration Patterns

**Pattern: Sequential Pipeline with Context Passing**

```
AGENT-01 (Researcher)
    │
    ├── OUTPUT: CandidateList (JSON structure)
    │
    ▼
AGENT-02 (Matcher)
    │
    ├── INPUT: CandidateList + JobRequirements
    ├── OUTPUT: RankedCandidateList (JSON structure)
    │
    ▼
AGENT-03 (Communicator)
    │
    ├── INPUT: RankedCandidateList + JobRequirements
    ├── OUTPUT: OutreachStrategy (JSON structure)
    │
    ▼
AGENT-04 (Reporter)
    │
    ├── INPUT: CandidateList + RankedCandidateList + OutreachStrategy + JobRequirements
    ├── OUTPUT: FinalReport (Markdown)
    │
    ▼
    candidate_report.md
```

**Context Passing**: Each agent receives the outputs of all preceding agents as context in its task description. CrewAI's sequential process handles this automatically via the `context` parameter on each task (PRD §4.1).

**Memory**: Agent memory is in-memory only for MVP. No persistent memory across workflow executions. Each run is stateless.

### 2.3 Tool Integration Needs

| Tool              | Purpose                                      | API Required    | Source   |
| ----------------- | -------------------------------------------- | --------------- | -------- |
| SerperDevTool     | Web search for candidate profiles            | SERPER_API_KEY  | PRD §4.8 |
| ScrapeWebsiteTool | Extract candidate information from web pages | None (built-in) | PRD §4.8 |

**Tool Error Handling**: If a tool fails (API rate limit, network error), the agent should retry with exponential backoff (PRD §5.2, NFR-002). If the tool is permanently unavailable, the agent should continue with available data and note the limitation in its output.

### 2.4 Task Orchestration Specification

**Execution Flow**: Sequential (TASK-01 → TASK-02 → TASK-03 → TASK-04) (PRD §4.1)

| Task ID | Agent    | Input Variables                      | Output              | Expected Time |
| ------- | -------- | ------------------------------------ | ------------------- | ------------- |
| TASK-01 | AGENT-01 | `{job_requirements}`                 | CandidateList       | < 90 seconds  |
| TASK-02 | AGENT-02 | `{job_requirements}`, TASK-01 output | RankedCandidateList | < 90 seconds  |
| TASK-03 | AGENT-03 | `{job_requirements}`, TASK-02 output | OutreachStrategy    | < 90 seconds  |
| TASK-04 | AGENT-04 | All previous outputs                 | FinalReport         | < 30 seconds  |

**Total Execution Time**: < 5 minutes end-to-end (PRD §5.1, NFR-001)

**Error Handling**:

- Retry failed tasks up to 3 times with exponential backoff (PRD §5.2)
- Log all errors with full context for debugging
- Produce partial report if intermediate task fails (graceful degradation)

### 2.5 CrewAI Framework Configuration

**Crew Assembly** (`crew.py`):

- Process type: Sequential (PRD §10, Assumption 7)
- Verbose logging: Enabled (PRD §5.3)
- Memory: In-memory (no persistent storage for MVP)
- Caching: Enabled for LLM responses (reduces API costs)
- Max RPM: Configurable per agent (default: 10)

**YAML Configuration Files**:

- `config/agents.yaml` — Agent role, goal, backstory definitions (PRD §6.4)
- `config/tasks.yaml` — Task descriptions, expected outputs, variable interpolation (PRD §6.5)

---

## 3. Frontend Architecture (CLI)

### 3.1 Technology Stack

| Component          | Technology    | Version       | Source   |
| ------------------ | ------------- | ------------- | -------- |
| Runtime            | Python        | >=3.10, <3.14 | PRD §6.2 |
| Dependency Manager | uv            | Latest        | PRD §6.2 |
| Agent Framework    | CrewAI        | >=1.15.1      | PRD §6.2 |
| Configuration      | YAML          | PyYAML        | PRD §6.2 |
| Environment        | python-dotenv | Latest        | PRD §4.8 |

### 3.2 Application Structure

```
recruitment-assistant/
├── .env.example                    # Environment variable template
├── .gitignore
├── pyproject.toml                  # Project dependencies
├── README.md                       # Setup and usage documentation
├── src/
│   └── recruitment/
│       ├── __init__.py
│       ├── main.py                 # Entry point and CLI
│       ├── crew.py                 # Crew assembly and orchestration
│       ├── config/
│       │   ├── agents.yaml         # Agent definitions
│       │   └── tasks.yaml          # Task definitions
│       └── tools/
│           ├── __init__.py
│           └── custom_tools.py     # Custom tool implementations
├── project-context/                # AAMAD artifacts
│   ├── 1.define/
│   │   ├── mrd.md
│   │   └── prd.md
│   ├── 2.build/
│   └── 3.deliver/
└── tests/                          # Test suite
```

**Source**: PRD §6.3

### 3.3 CLI Interface Design

**Input Flow** (PRD §4.2, FR-002):

1. User runs `python -m recruitment.main` or `uv run recruitment`
2. System prompts for job description input
3. User pastes job description (natural language or structured format)
4. System validates required fields: title, description, responsibilities, qualifications
5. System confirms receipt and begins workflow execution

**Required Input Fields** (PRD §4.2):

- Job title (required)
- Job description — minimum 100 characters (required)
- Key responsibilities — minimum 3 items (required)
- Required qualifications — minimum 3 items (required)
- Preferred qualifications (optional)
- Perks and benefits (optional)

**Progress Display** (PRD §4.7):

- Agent name and current task status
- Task completion percentage
- Elapsed time counter
- Error messages with actionable guidance

**Output Display** (PRD §4.6):

- Formatted markdown report in terminal
- File path confirmation for `candidate_report.md`
- Execution summary (time, agents used, tasks completed)

### 3.4 Post-MVP: Web Chat UI

The web chat UI is explicitly deferred to v0.2.0 (PRD §8.2). When implemented, it will use:

| Component        | Technology                | Source      |
| ---------------- | ------------------------- | ----------- |
| Framework        | Next.js latest App Router | Template §3 |
| UI Library       | assistant-ui + shadcn/ui  | Template §3 |
| Styling          | Tailwind CSS              | Template §3 |
| State Management | Zustand                   | Template §3 |

**Integration Pattern** (for future reference):

- Next.js API routes call Python CrewAI service
- Streaming responses via Server-Sent Events (SSE)
- assistant-ui renders streaming agent output
- Custom tool components display agent actions

**This section is documented here for planning purposes only. No web UI code is included in the MVP scope.**

---

## 4. Backend Architecture

### 4.1 API Architecture

**MVP: No API Layer**

The MVP is a direct Python CLI application. There is no HTTP API, no server process, and no request/response abstraction. The user interacts directly with the CrewAI runtime through the CLI.

**Post-MVP API Design** (for reference):

- Next.js API routes for agent communication
- Streaming response handling via SSE
- Request/response JSON structures
- Rate limiting and security middleware

### 4.2 CrewAI Python Service Layer

**Entry Point** (`main.py`):

```python
# Pseudocode structure
def main():
    job_requirements = collect_input()      # CLI prompt
    validate_input(job_requirements)        # Input validation
    crew = assemble_crew()                  # Load agents from YAML
    result = crew.kickoff(inputs={...})     # Execute workflow
    save_report(result)                     # Write candidate_report.md
    display_summary(result)                 # CLI output
```

**Crew Assembly** (`crew.py`):

```python
# Pseudocode structure
from crewai import Agent, Task, Crew, Process

# Load agents from config/agents.yaml
# Load tasks from config/tasks.yaml
# Assemble Crew with Sequential process
# Configure verbose, memory, caching
```

**Source**: PRD §6.1, PRD §6.3

### 4.3 Database Architecture

**MVP: No Database**

All data is file-based:

- Configuration: YAML files in `config/`
- Environment: `.env` file
- Output: `candidate_report.md` in project root
- Logs: Console output (stdout/stderr)

**Post-MVP Database Path** (for reference):

- SQLite for conversation history and analytics (Template §4)
- Schema: conversations, messages, agent_runs, task_outputs
- Migration strategy: Alembic
- Data retention: 90 days default

### 4.4 Configuration Management

**Configuration Files** (PRD §4.8):

| File                 | Purpose                           | Format    |
| -------------------- | --------------------------------- | --------- |
| `config/agents.yaml` | Agent role, goal, backstory       | YAML      |
| `config/tasks.yaml`  | Task description, expected output | YAML      |
| `.env`               | API keys, LLM settings            | Key-Value |
| `pyproject.toml`     | Python dependencies               | TOML      |

**Environment Variables** (PRD §4.8):

| Variable       | Required                             | Default              | Description                                                         |
| -------------- | ------------------------------------ | -------------------- | ------------------------------------------------------------------- |
| OPENAI_API_KEY | Yes (if using OpenAI-compatible API) | —                    | API key for OpenAI-compatible endpoint (e.g., https://api.iamhc.cn) |
| SERPER_API_KEY | Yes                                  | —                    | Serper.dev API key                                                  |
| LLM_MODEL      | No                                   | glm-5.2              | LLM model identifier                                                |
| LLM_BASE_URL   | No                                   | https://api.iamhc.cn | Custom LLM endpoint (OpenAI-compatible, Ollama, etc.)               |

---

## 5. DevOps & Deployment

### 5.1 CI/CD Pipeline

**MVP: Local Development Only**

No CI/CD pipeline is required for MVP. The application runs locally via `uv run recruitment`. Testing is manual.

**Post-MVP CI/CD** (for reference):

- GitHub Actions workflow
- Build: `uv sync` + `pytest`
- Test: Unit + integration tests
- Deploy: Docker container to cloud provider

### 5.2 Infrastructure Requirements

**Compute**:

- Python runtime: >=3.10, <3.14
- Memory: 4 GB minimum (LLM inference + agent execution)
- Storage: 100 MB for application + dependencies
- Network: Internet access for LLM API (GLM-5.2 / OpenAI-compatible), Serper.dev API

**No containerization or cloud infrastructure for MVP.**

### 5.3 Monitoring & Observability

**MVP Monitoring**:

- Verbose logging to console (PRD §5.3)
- Agent reasoning traces in output
- Task execution time tracking
- Error messages with stack traces

**Post-MVP Monitoring** (for reference):

- Application performance monitoring (APM)
- Log aggregation (ELK, Datadog)
- Alerting rules for failures
- Dashboard for execution metrics

---

## 6. Data Flow & Integration

### 6.1 Request/Response Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   User CLI   │────>│   main.py    │────>│   crew.py    │
│   Input      │     │   Validate   │     │   Assemble   │
└──────────────┘     └──────────────┘     └──────────────┘
                                                │
                                                ▼
                                         ┌──────────────┐
                                         │   CrewAI     │
                                         │   Sequential │
                                         │   Process    │
                                         └──────────────┘
                                                │
                    ┌───────────────────────────┼───────────────────────────┐
                    │                           │                           │
                    ▼                           ▼                           ▼
             ┌──────────────┐          ┌──────────────┐          ┌──────────────┐
             │  TASK-01     │          │  TASK-02     │          │  TASK-03     │
             │  Researcher  │──────>   │  Matcher     │──────>   │  Communicator│
             └──────────────┘          └──────────────┘          └──────────────┘
                    │                           │                           │
                    ▼                           ▼                           ▼
             ┌──────────────┐          ┌──────────────┐          ┌──────────────┐
             │  SerperDev   │          │  SerperDev   │          │  SerperDev   │
             │  ScrapeWeb   │          │  ScrapeWeb   │          │  ScrapeWeb   │
             └──────────────┘          └──────────────┘          └──────────────┘
                    │                           │                           │
                    └───────────────────────────┼───────────────────────────┘
                                                │
                                                ▼
                                         ┌──────────────┐
                                         │  TASK-04     │
                                         │  Reporter    │
                                         └──────────────┘
                                                │
                                                ▼
                                         ┌──────────────┐
                                         │  candidate_  │
                                         │  report.md   │
                                         └──────────────┘
```

### 6.2 Data Transformation

**Input Data Structure**:

```json
{
  "job_requirements": {
    "title": "Senior Python Developer",
    "description": "...",
    "responsibilities": ["...", "...", "..."],
    "required_qualifications": ["...", "...", "..."],
    "preferred_qualifications": ["..."],
    "perks": ["..."]
  }
}
```

**Inter-Agent Data Flow**:

- TASK-01 output: CandidateList (structured candidate profiles)
- TASK-02 output: RankedCandidateList (candidates with scores and ranks)
- TASK-03 output: OutreachStrategy (templates and personalization)
- TASK-04 output: FinalReport (markdown document)

### 6.3 External Integrations

| Integration                         | API  | Authentication | Rate Limits                | Source   |
| ----------------------------------- | ---- | -------------- | -------------------------- | -------- |
| GLM-5.2 (via OpenAI-compatible API) | REST | API Key        | Provider-dependent         | PRD §9.1 |
| Serper.dev                          | REST | API Key        | 2,500 queries/month (free) | PRD §9.1 |
| Web Scraping                        | HTTP | None           | Respect robots.txt         | PRD §4.3 |

**Error Handling for External APIs** (PRD §5.2):

- Retry with exponential backoff (1s, 2s, 4s, max 3 retries)
- Graceful degradation if tool unavailable
- Log all API errors with request/response details

---

## 7. Performance & Scalability

### 7.1 Performance Requirements

| Metric                      | Target                | Source             |
| --------------------------- | --------------------- | ------------------ |
| End-to-end execution time   | < 5 minutes           | PRD §5.1 (NFR-001) |
| Agent task completion time  | < 90 seconds per task | PRD §5.1 (NFR-001) |
| Report generation time      | < 30 seconds          | PRD §5.1 (NFR-001) |
| Concurrent workflow support | 1 user (MVP)          | PRD §5.1 (NFR-001) |
| Workflow completion rate    | >= 95%                | PRD §5.2 (NFR-002) |
| Setup time                  | < 15 minutes          | PRD §5.4 (NFR-004) |
| Time to first run           | < 30 minutes          | PRD §5.4 (NFR-004) |

### 7.2 Performance Optimization Strategies

1. **LLM Response Caching**: Cache LLM responses for repeated prompts to reduce API costs and latency.
2. **Concurrent Web Requests**: Use async HTTP clients for SerperDevTool and ScrapeWebsiteTool where possible.
3. **Structured Output Validation**: Validate agent outputs against expected schemas to catch errors early.
4. **Timeout Configuration**: Set per-task timeouts to prevent runaway agent execution.

### 7.3 Scalability Architecture

**MVP: Single-User, Single-Execution**

The architecture is not designed for horizontal scaling in MVP. Each execution is a standalone process.

**Post-MVP Scaling Triggers** (for reference):

- Concurrent users > 1: Add API layer + worker pool
- Execution time > 5 min: Optimize LLM prompts, add caching
- Agent count > 4: Consider hierarchical process with manager agent

---

## 8. Security & Compliance

### 8.1 Security Framework

**API Key Security** (PRD §5.3, NFR-003):

- All API keys stored in `.env` file (never in code)
- `.env` added to `.gitignore` (never committed)
- `.env.example` committed as template
- No API keys logged or displayed in output

**Data Privacy** (PRD §1.3, Principle 5):

- Candidate data processed locally only
- No external storage of candidate information
- Support for local LLM deployment (Ollama, LM Studio)
- No telemetry or analytics in MVP

**Input Validation** (PRD §4.2):

- Validate job description completeness before execution
- Reject empty or malformed inputs
- Sanitize user input to prevent injection attacks

### 8.2 GDPR Considerations

From MRD §9:

- **Data Minimization**: Only collect candidate information necessary for evaluation
- **Right to Erasure**: Candidate data is not persisted; all data is transient during execution
- **Transparency**: Agent reasoning traces provide auditability
- **Local Processing**: Support for on-premise deployment avoids data transfer to third parties

**MVP Compliance Gap**: No formal GDPR compliance audit is performed. Document compliance gaps for post-MVP remediation (PRD §13, Open Question 3).

### 8.3 Audit Trail

- All agent reasoning traces logged to console (PRD §5.3)
- Task inputs and outputs logged for debugging
- No persistent audit log in MVP (post-MVP: SQLite-based audit trail)

---

## 9. Testing & Quality Assurance

### 9.1 Testing Strategy

| Test Type         | Scope                                         | Tool          | Coverage Target | Source           |
| ----------------- | --------------------------------------------- | ------------- | --------------- | ---------------- |
| Unit Tests        | Individual functions, tools, input validation | pytest        | >= 80%          | PRD §7.5 (F-040) |
| Integration Tests | Agent workflow, task dependencies             | pytest        | Key paths       | PRD §7.5 (F-041) |
| End-to-End Tests  | Full workflow from input to report            | pytest        | 1 critical path | PRD §7.5 (F-042) |
| Performance Tests | Execution time benchmarks                     | Manual timing | All tasks       | PRD §7.5 (F-043) |

**Source**: PRD §7.5 (Epic 5), PRD §12.2

### 9.2 Test Coverage Target

**Minimum: 80%** (PRD §12.2)

Priority coverage areas:

1. Input validation logic (PRD §4.2)
2. Tool error handling (PRD §5.2)
3. Agent configuration loading (PRD §4.8)
4. Report generation (PRD §4.6)

### 9.3 Quality Gates

- All unit tests pass
- No linting errors (ruff)
- Type checking passes (mypy)
- Documentation complete for all features (PRD §12.2)
- Manual end-to-end test produces valid report

### 9.4 Test File Structure

```
tests/
├── __init__.py
├── conftest.py
├── test_input_validation.py
├── test_tools.py
├── test_agents.py
├── test_workflow.py
└── test_report_generation.py
```

---

## 10. MVP Launch & Feedback Strategy

### 10.1 Milestone Timeline

**2-Week Sprint** (PRD §8.1):

| Milestone                | Duration  | Deliverables                                | Source   |
| ------------------------ | --------- | ------------------------------------------- | -------- |
| M1: Project Setup        | Day 1-2   | Scaffolding, dependencies, configuration    | PRD §8.1 |
| M2: Agent Implementation | Day 3-5   | 4 agents with tools, YAML configs           | PRD §8.1 |
| M3: Workflow Integration | Day 6-8   | Sequential process, input/output flow       | PRD §8.1 |
| M4: CLI Interface        | Day 9-10  | User input, progress display, report output | PRD §8.1 |
| M5: Testing & Polish     | Day 11-14 | Tests, documentation, bug fixes             | PRD §8.1 |

### 10.2 Success Metrics

**Product Metrics** (PRD §12.1):

| Metric                   | MVP Target  | Measurement                  |
| ------------------------ | ----------- | ---------------------------- |
| Workflow completion rate | >= 95%      | Successful runs / total runs |
| Report generation time   | < 5 minutes | Average end-to-end time      |
| Candidate quality score  | >= 3.5/5    | Recruiter review rating      |
| User satisfaction (NPS)  | >= 40       | Post-usage survey            |
| Time-to-fill reduction   | >= 30%      | Compared to baseline         |

**Technical Metrics** (PRD §12.2):

| Metric                     | Target       | Measurement                |
| -------------------------- | ------------ | -------------------------- |
| Test coverage              | >= 80%       | Unit + integration tests   |
| Documentation completeness | 100%         | All features documented    |
| Setup time                 | < 15 minutes | First-time user onboarding |
| Error rate                 | < 5%         | Failed workflow runs       |

### 10.3 Beta Testing Strategy

**User Selection**:

- Internal testing by development team
- 2-3 recruited recruiters for external validation (if available within sprint)
- Focus on technical users comfortable with CLI

**Feedback Collection**:

- Post-execution survey (NPS, quality rating)
- Bug reports via GitHub Issues
- Feature requests tracked for post-MVP

**Feature Flags**:

- LLM provider selection (GLM-5.2 / OpenAI-compatible vs. Ollama)
- Verbose logging toggle
- Report format options (markdown vs. JSON)

### 10.4 Post-MVP Roadmap

| Version | Features                                  | Target  | Source   |
| ------- | ----------------------------------------- | ------- | -------- |
| v0.2.0  | Web chat UI (Next.js + assistant-ui)      | Month 2 | PRD §8.2 |
| v0.3.0  | ATS integration (Greenhouse, Lever)       | Month 3 | PRD §8.2 |
| v0.4.0  | Multi-role hiring support                 | Month 4 | PRD §8.2 |
| v0.5.0  | Analytics dashboard                       | Month 5 | PRD §8.2 |
| v1.0.0  | Production-ready with auth, multi-tenancy | Month 6 | PRD §8.2 |

---

## Architecture Validation Checklist

- [x] All PRD requirements mapped to architectural components (PRD §4, §5, §7)
- [x] CrewAI agents properly designed (PRD §4.1, §6.4)
- [x] CLI interface supports required patterns (PRD §4.7)
- [x] Python architecture optimized for simplicity (PRD §6.3)
- [x] File-based output supports required formats (PRD §4.6)
- [x] Configuration system follows YAML standards (PRD §4.8)
- [x] Security measures appropriate for MVP (PRD §5.3)
- [x] Testing strategy supports rapid iteration (PRD §7.5)
- [x] Monitoring provides actionable insights (PRD §5.3)
- [x] Architecture supports MVP to production transition (PRD §8.2)

---

## Assumptions

1. **AAMAD_TARGET_RUNTIME = crewai**: CrewAI is the primary runtime framework (PRD §10, MRD §10).
2. **MVP is CLI-first**: Web UI is explicitly deferred to v0.2.0 (PRD §2.1, Assumption 2).
3. **Single-user MVP**: No multi-tenancy or authentication (PRD §2.1, Assumption 3).
4. **GLM-5.2 default**: Users must have access to the GLM-5.2 API endpoint (https://api.iamhc.cn) or configure an alternative LLM (PRD §10, Assumption 4).
5. **Serper.dev required**: Web search is essential for candidate research (PRD §10, Assumption 5).
6. **No LinkedIn scraping**: Production LinkedIn scraping violates ToS; MVP uses compliant sources only (PRD §10, Assumption 6).
7. **Sequential process**: Hierarchical process with manager agent is deferred (PRD §10, Assumption 7).
8. **2-week sprint**: MVP delivery within 14 calendar days (PRD §8.1).
9. **Local execution only**: No cloud deployment, containerization, or CI/CD for MVP.
10. **No database**: All data is file-based for MVP.

---

## Open Questions

1. **Web UI Priority**: Should the web chat UI be included in MVP or deferred?
   - _Decision_: Deferred to v0.2.0 (PRD §13, Open Question 1).
   - _Impact_: Reduces scope, accelerates MVP delivery.

2. **LLM Model Selection**: Should we support multiple LLM providers in MVP or focus on GLM-5.2?
   - _Decision_: Support GLM-5.2 (OpenAI-compatible) + Ollama in MVP; extend post-MVP (PRD §13, Open Question 2).
   - _Impact_: LiteLLM compatibility enables provider switching without code changes.

3. **Compliance Requirements**: What level of GDPR/EEOC compliance is required for MVP?
   - _Decision_: Document compliance gaps; address in v0.3.0+ (PRD §13, Open Question 3).
   - _Impact_: Local processing minimizes compliance risk.

4. **Pricing Model**: Should the MVP be free/open-source or include a commercial tier?
   - _Decision_: Free/open-source; commercial features in enterprise tier (PRD §13, Open Question 4).
   - _Impact_: MIT license aligns with CrewAI ecosystem.

---

## Audit

| Field                   | Value                                              |
| ----------------------- | -------------------------------------------------- |
| AAMAD_TARGET_RUNTIME    | crewai                                             |
| Source Artifacts        | prd.md (v1.0), mrd.md (v1.0)                       |
| PRD Sections Referenced | §1, §2, §4, §5, §6, §7, §8, §9, §10, §11, §12, §13 |
| MRD Sections Referenced | §5, §9, §10                                        |
| Template Source         | .opencode/commands/generate-sad.md                 |
| Assumptions Recorded    | 10                                                 |
| Open Questions Recorded | 4                                                  |

---

_This SAD defines the MVP architecture for the Recruitment Assistant application. Implementation will proceed in AAMAD Phase 2 following the Architecture Plan._
