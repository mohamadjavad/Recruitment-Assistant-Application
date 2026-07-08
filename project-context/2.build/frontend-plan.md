# Frontend Plan

## Recruitment Assistant — CLI Interface (Step 2)

**Document Version:** 1.0  
**Date:** July 8, 2026  
**Owner:** @frontend.eng  
**Status:** ✅ COMPLETED  
**Estimated Effort:** Day 9-10 (PRD §8.1, M4)

---

## 1. Overview

This document defines the frontend implementation plan for the Recruitment Assistant CLI interface. Despite being assigned to @frontend.eng, this step builds the CLI interface (not a web UI). The web chat UI is deferred to v0.2.0 (PRD §8.2).

**Reference Documents:**
- PRD: project-context/1.define/prd.md (§4.2, §4.7, §7.3)
- SAD: project-context/2.build/sad.md (§3.3)
- Architecture Plan: project-context/2.build/architecture-plan.md (Step 2)

---

## 2. UI Components to Build

### 2.1 CLI Entry Point (`main.py`)

| Component | Description | Status |
|-----------|-------------|--------|
| Command-line argument parsing | Parse optional flags (--verbose, --help) | ✅ Implemented |
| Interactive job description input | Structured prompts for all required fields | ✅ Implemented |
| Input validation | PRD §4.2 validation rules | ✅ Implemented |
| Progress display | Rich library progress indicators | ✅ Implemented |
| Formatted report display | Markdown rendering in terminal | ✅ Implemented |
| Report file save | Write to candidate_report.md | ✅ Implemented |
| Error handling | Actionable error messages | ✅ Implemented |

### 2.2 Crew Assembly Stub (`crew.py`)

| Component | Description | Status |
|-----------|-------------|--------|
| YAML config loading | Load agents.yaml and tasks.yaml | ✅ Implemented |
| Agent creation | Create CrewAI Agent objects from config | ✅ Implemented |
| Task creation | Create CrewAI Task objects with variable interpolation | ✅ Implemented |
| Crew assembly | Sequential process configuration | ✅ Implemented |
| kickoff() method | Execute workflow with job_requirements input | ✅ Implemented |
| Placeholder for tools | SerperDevTool, ScrapeWebsiteTool stubs | ✅ Implemented |

### 2.3 Input Components

| Component | Description | PRD Reference |
|-----------|-------------|---------------|
| Job Title Prompt | Required text input | PRD §4.2 |
| Job Description Input | Multi-line text (min 100 chars) | PRD §4.2 |
| Responsibilities Input | List input (min 3 items) | PRD §4.2 |
| Qualifications Input | List input (min 3 items) | PRD §4.2 |
| Preferred Qualifications | Optional list input | PRD §4.2 |
| Perks and Benefits | Optional list input | PRD §4.2 |
| Confirmation Prompt | Confirm before execution | — |

### 2.4 Display Components

| Component | Description | PRD Reference |
|-----------|-------------|---------------|
| Welcome Panel | Project title and description | PRD §4.7 |
| Input Summary Table | Tabular display of collected input | — |
| Progress Spinner | During workflow execution | PRD §4.7 |
| Agent Status Display | Current agent and task name | PRD §4.7 |
| Elapsed Time Counter | Time since workflow start | PRD §4.7 |
| Report Panel | Formatted markdown output | PRD §4.6 |
| Error Panel | Actionable error messages | PRD §5.4 |
| File Path Confirmation | Save location display | PRD §4.6 |

---

## 3. User Interaction Flows

### 3.1 Primary Flow: Input → Validation → Execution → Output

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER RUNS CLI COMMAND                         │
│              uv run recruitment                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ENVIRONMENT CHECK                             │
│         Verify OPENAI_API_KEY (GLM-5.2 via iamhc.cn) and SERPER_API_KEY │
│         If missing → Display setup instructions → Exit           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COLLECT JOB DESCRIPTION                       │
│         Interactive prompts for all required fields              │
│         Multi-line input for description                         │
│         List input for responsibilities/qualifications           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATE INPUT                                │
│         Check all required fields present                        │
│         Validate minimum lengths                                 │
│         If invalid → Display errors → Re-prompt                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONFIRM AND EXECUTE                           │
│         Display summary table                                    │
│         User confirms → Start workflow                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DISPLAY PROGRESS                              │
│         Spinner with agent name and task status                  │
│         Elapsed time counter                                     │
│         Error messages with actionable guidance                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DISPLAY REPORT                                │
│         Formatted markdown in terminal                           │
│         File path confirmation                                   │
│         Execution summary                                        │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Error Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ERROR OCCURS                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLASSIFY ERROR                                │
│         Input validation error → Re-prompt                       │
│         API error → Retry with backoff                           │
│         Tool error → Graceful degradation                        │
│         Fatal error → Display message → Exit                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. API Integration Points

### 4.1 CrewAI Crew Integration

| Integration Point | Method | Input | Output |
|-------------------|--------|-------|--------|
| Crew assembly | `RecruitmentCrew.__init__()` | config_dir | Crew object |
| Workflow execution | `RecruitmentCrew.kickoff()` | job_requirements | Final report string |
| Config loading | `_load_config()` | filename | YAML dict |

### 4.2 External API Integration (via CrewAI Tools)

| API | Tool | Purpose | Auth |
|-----|------|---------|------|
| GLM-5.2 (via https://api.iamhc.cn) | CrewAI LLM (OpenAI-compatible) | Agent reasoning | OPENAI_API_KEY |
| Serper.dev | SerperDevTool | Web search | SERPER_API_KEY |
| Web Scraping | ScrapeWebsiteTool | Profile extraction | None |

### 4.3 File I/O Integration

| Operation | Path | Format |
|-----------|------|--------|
| Read config | `src/recruitment/config/*.yaml` | YAML |
| Write report | `./candidate_report.md` | Markdown |
| Read env | `.env` | Key-Value |

---

## 5. Implementation Approach

### 5.1 Technology Stack

| Component | Technology | Version | Source |
|-----------|-----------|---------|--------|
| Language | Python | >=3.10 | PRD §6.2 |
| CLI Library | rich | >=13.0.0 | PRD §4.7 |
| Config Loading | PyYAML | >=6.0 | PRD §4.8 |
| Env Management | python-dotenv | >=1.0.0 | PRD §4.8 |
| Agent Framework | CrewAI | >=1.15.1 | PRD §6.2 |

### 5.2 Rich Library Usage

| Rich Component | Usage |
|----------------|-------|
| `Console` | Terminal output management |
| `Panel` | Bordered content display (welcome, errors, report) |
| `Table` | Tabular data display (input summary) |
| `Prompt` | Interactive text input |
| `Confirm` | Yes/No confirmation prompts |
| `Spinner` | Progress indicators during execution |
| `Markdown` | Render markdown report in terminal |
| `Progress` | Multi-step progress bars |

### 5.3 Input Validation Strategy

Per PRD §4.2:
- **Job Title**: Required, non-empty string
- **Job Description**: Required, minimum 100 characters
- **Responsibilities**: Required, minimum 3 items
- **Qualifications**: Required, minimum 3 items
- **Preferred Qualifications**: Optional list
- **Perks and Benefits**: Optional list

Validation is performed immediately after collection. If validation fails, the user is prompted to correct specific issues.

### 5.4 Error Handling Strategy

Per PRD §5.2:
- **Input Errors**: Re-prompt with specific guidance
- **API Errors**: Retry with exponential backoff (1s, 2s, 4s, max 3 retries)
- **Tool Errors**: Graceful degradation, continue with available data
- **Fatal Errors**: Display message and exit with code 1

---

## 6. File Structure

```
recruitment-assistant/
├── src/recruitment/
│   ├── __init__.py              # Package metadata
│   ├── main.py                  # CLI entry point (ENHANCED)
│   ├── crew.py                  # Crew assembly stub (ENHANCED)
│   ├── config/
│   │   ├── agents.yaml          # Agent definitions
│   │   └── tasks.yaml           # Task definitions
│   └── tools/
│       ├── __init__.py
│       └── custom_tools.py      # Custom tool implementations
├── pyproject.toml               # Dependencies and scripts
└── .env                         # Environment variables
```

---

## 7. Status Tracking

| Component | Status | Notes |
|-----------|--------|-------|
| frontend-plan.md | ✅ COMPLETED | This document |
| main.py enhancements | ✅ COMPLETED | Full CLI interface with progress display |
| crew.py stub | ✅ COMPLETED | Working structure with placeholder tools |
| Input validation | ✅ COMPLETED | PRD §4.2 compliant |
| Progress display | ✅ COMPLETED | Rich library spinner and status |
| Report display | ✅ COMPLETED | Markdown rendering in terminal |
| Error handling | ✅ COMPLETED | Actionable error messages |
| File save | ✅ COMPLETED | candidate_report.md output |

---

## 8. Decisions and Trade-offs

### Decision 1: Rich Library for CLI Output
- **Rationale**: Rich provides beautiful terminal output with minimal code. Supports markdown rendering, tables, panels, and spinners.
- **Trade-off**: Adds dependency, but it's lightweight and well-maintained.

### Decision 2: Interactive Prompts vs. YAML Input
- **Rationale**: Interactive prompts are more user-friendly for MVP. YAML input could be added as an advanced option post-MVP.
- **Trade-off**: More code for input handling, but better UX.

### Decision 3: Sequential Validation
- **Rationale**: Validate each field immediately after collection to provide immediate feedback.
- **Trade-off**: Slightly more complex flow, but better user experience.

### Decision 4: Crew.py as Stub
- **Rationale**: The crew.py implements the full structure but with placeholder tool integration. @backend.eng will replace the tool initialization with real implementations.
- **Trade-off**: Code may need modification when real tools are integrated, but the structure is sound.

---

## 9. Next Steps

1. **@backend.eng**: Implement real agent and tool configurations in crew.py
2. **@integration.eng**: Connect CLI input to crew.kickoff() with real execution
3. **@qa.eng**: Test input validation, error handling, and end-to-end flow

---

*This document guides the frontend implementation for the Recruitment Assistant CLI interface. All decisions are traceable to PRD and SAD requirements.*
