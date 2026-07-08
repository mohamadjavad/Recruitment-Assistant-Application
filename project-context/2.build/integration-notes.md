# Integration Notes

## Recruitment Assistant — Step 4: Integration

**Date:** July 8, 2026  
**Owner:** @integration.eng  
**Status:** COMPLETED

---

## 1. Integration Overview

This document describes how `main.py` (CLI) and `crew.py` (CrewAI workflow) are wired together, the data flow between them, and the integration test results.

### Runtime: CrewAI (AAMAD_TARGET_RUNTIME = crewai)

The integration uses CrewAI's native Python API directly — no HTTP layer, no message queues, no streaming. The CLI calls `crew.kickoff()` synchronously and receives the final report as a string.

---

## 2. Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User CLI Input                        │
│              (main.py: collect_job_description_interactive)│
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Input Validation                            │
│          (main.py: validate_job_description)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Format Job Requirements                     │
│      (main.py: format_job_requirements → str)            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Crew Assembly                               │
│     (crew.py: RecruitmentCrew.__init__ → load YAML)      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Execute Workflow                             │
│     (crew.py: crew.kickoff(job_requirements) → str)      │
│                                                          │
│  AGENT-01 (Researcher) → TASK-01                         │
│       │                                                  │
│       ▼                                                  │
│  AGENT-02 (Matcher) → TASK-02 (context: TASK-01)         │
│       │                                                  │
│       ▼                                                  │
│  AGENT-03 (Communicator) → TASK-03 (context: TASK-01,02) │
│       │                                                  │
│       ▼                                                  │
│  AGENT-04 (Reporter) → TASK-04 (context: all prior)      │
│                                                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Report Display & Save                       │
│     (main.py: display_report + save to .md file)         │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Integration Points

### 3.1 main.py → crew.py (Input)

**Method:** `main.py:run_workflow(job_desc: dict)` calls `crew.kickoff(job_requirements: str)`

**Data transformation:**
1. `main.py` collects `job_desc` as a dict with keys: `title`, `description`, `responsibilities`, `qualifications`, `preferred_qualifications`, `perks`
2. `main.py` calls `format_job_requirements(job_desc)` to produce a formatted string
3. The formatted string is passed to `crew.kickoff(job_requirements)`

**Contract:**
- Input: `str` — formatted job requirements (non-empty)
- Output: `str` — markdown report
- Error: `ValueError` if input is empty/whitespace

### 3.2 crew.py → main.py (Output)

**Return value:** `crew.kickoff()` returns the final report as a string (normalized from CrewAI's `AgentOutput` or raw string).

**Normalization logic in crew.py:**
```python
result = self._crew.kickoff()
if hasattr(result, "raw"):
    return result.raw
return str(result)
```

### 3.3 Variable Interpolation (YAML → Python)

**Pattern:** Tasks in `tasks.yaml` use `{job_requirements}` as a placeholder. `crew.py` interpolates this via `str.format()`:

```python
description = task_config["description"].format(job_requirements=job_requirements)
```

**Verified tasks with `{job_requirements}`:**
- `research_candidates_task` — has placeholder
- `match_and_score_candidates_task` — has placeholder
- `outreach_strategy_task` — has placeholder
- `report_candidates_task` — NO placeholder (synthesis task, gets context from prior tasks)

### 3.4 Context Passing (Task → Task)

CrewAI's `context` parameter chains task outputs:
- TASK-01: no context (first task)
- TASK-02: context = [TASK-01]
- TASK-03: context = [TASK-01, TASK-02]
- TASK-04: context = [TASK-01, TASK-02, TASK-03]

### 3.5 Error Handling

| Error Source | Handler | Behavior |
|---|---|---|
| Missing API keys | `main.py:main()` checks env vars at startup (expects `OPENAI_API_KEY` for GLM-5.2 via iamhc.cn, `SERPER_API_KEY` for web search) | Exits with actionable message |
| Invalid input | `main.py:validate_job_description()` | Displays errors, exits |
| Empty job requirements | `crew.py:kickoff()` | Raises `ValueError` |
| Tool unavailable | `custom_tools.py:get_tools_for_agent()` | Skips tool gracefully, agent uses LLM knowledge |
| CrewAI execution error | `main.py:run_workflow()` try/except | Displays error with technical details |

---

## 4. Integration Issues Found & Resolved

**No blocking issues found.** The integration between `main.py` and `crew.py` is clean:

1. **Data structure match**: `format_job_requirements()` produces exactly the string format that `crew.kickoff()` expects.
2. **YAML config alignment**: All 4 agent keys and 4 task keys match between YAML files and `crew.py` mappings.
3. **Import chain**: `main.py` imports `RecruitmentCrew` from `crew.py` at runtime (in `run_workflow()`), avoiding circular imports.
4. **Output normalization**: `crew.kickoff()` handles both `AgentOutput` and raw string returns from CrewAI.

**Observation (not a bug):** The `report_candidates_task` in `tasks.yaml` does not use `{job_requirements}` because it's the final synthesis task that receives context from all previous tasks. This is by design per SAD §2.2.

**CrewAI deprecation warnings:** Some CrewAI internals produce deprecation warnings (e.g., `function_calling_llm`, `allow_code_execution`). These are cosmetic and do not affect functionality.

---

## 5. Testing

### 5.1 Integration Test Suite

**File:** `tests/test_integration.py`  
**Tests:** 66 tests across 14 test classes  
**Result:** All 66 pass

| Test Class | Count | What it validates |
|---|---|---|
| TestImports | 4 | All modules import correctly |
| TestCrewInitialization | 6 | YAML config loading, agent/task structure |
| TestInputValidation | 9 | Valid/invalid job descriptions |
| TestFormatJobRequirements | 7 | String formatting of job requirements |
| TestYAMLConfigIntegrity | 5 | YAML structure, placeholders, counts |
| TestAgentCreation | 3 | CrewAI Agent creation from config |
| TestTaskCreation | 3 | CrewAI Task creation, interpolation, context |
| TestCrewAssembly | 3 | Crew assembly with agents and tasks |
| TestToolAvailability | 5 | Tool factory, reporter has no tools |
| TestDataFlow | 4 | Dict → string → crew acceptance |
| TestEnvironmentHandling | 2 | Env var checks, dotenv loading |
| TestIntegrationSeam | 5 | Code inspection of main.py → crew.py wiring |
| TestErrorHandling | 6 | Exception classes, display functions |
| TestRetryDecorator | 4 | Exponential backoff decorator |

### 5.2 Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run only integration tests
uv run pytest tests/test_integration.py -v

# Run specific test class
uv run pytest tests/test_integration.py::TestImports -v
```

### 5.3 Existing Tests Unaffected

All 6 tests in `tests/test_basic.py` continue to pass alongside the 66 new integration tests (72 total).

---

## 6. Manual Verification

### 6.1 Import Check
```
✓ uv run python -c "from recruitment.main import main; print('Import OK')"
✓ uv run python -c "from recruitment.crew import RecruitmentCrew; c = RecruitmentCrew(); print('Crew OK')"
```

### 6.2 Full Test Suite
```
✓ 72 passed, 124 warnings in 8.16s
```

---

## 7. Testing Instructions

To run the integration tests locally:

```bash
cd recruitment-assistant

# Ensure dependencies are installed
uv sync

# Run the full test suite
uv run pytest tests/ -v

# Run only integration tests
uv run pytest tests/test_integration.py -v

# Run with coverage (if pytest-cov installed)
uv run pytest tests/test_integration.py --cov=recruitment --cov-report=term-missing
```

---

## 8. Caveats & Notes

1. **No actual API calls in tests**: Integration tests validate the wiring (imports, data flow, config loading, agent/task creation) but do NOT execute `crew.kickoff()` with real API calls. Full end-to-end execution requires valid API keys (`OPENAI_API_KEY` for GLM-5.2 via iamhc.cn, `SERPER_API_KEY` for web search). The `LLM_BASE_URL` must be set to `https://api.iamhc.cn/v1` when using the GLM-5.2 model (as configured in `.env` via `LLM_MODEL=glm-5.2`).

2. **CrewAI warnings**: Deprecation warnings from CrewAI internals are cosmetic. They originate from CrewAI's own code and do not affect our integration.

3. **Report output location**: `main.py` saves `candidate_report.md` to the current working directory (not necessarily the project root). This is by design for CLI usage.

4. **No external integrations**: The integration is purely internal (main.py ↔ crew.py). No third-party services are called during integration testing.

---

*This document describes the integration between the CLI frontend and CrewAI backend for the Recruitment Assistant MVP.*
