# Architecture Plan

## Recruitment Assistant Application — Phase 2 Build

**Document Version:** 1.0  
**Date:** July 7, 2026  
**Prepared by:** @system.arch (AAMAD Phase 2 — Build)  
**Input Sources:** project-context/2.build/sad.md, project-context/1.define/prd.md, project-context/1.define/mrd.md  
**AAMAD_TARGET_RUNTIME:** crewai

---

## 1. Implementation Approach

This Architecture Plan translates the System Architecture Document (SAD) into an ordered build sequence for AAMAD Phase 2. The plan follows the AAMAD workflow: Definition is complete (Phase 1), Architecture is defined (this document), and Build execution proceeds through agent-assigned steps.

### 1.1 Build Philosophy

- **Sequential Execution**: Each step depends on the prior step's completion. No parallel work is possible until the backend foundation is established.
- **MVP Scope Discipline**: Only features explicitly listed in PRD §2.1 (In Scope) are implemented. No scope creep.
- **Test-Alongside Development**: Unit tests are written with each feature, not deferred to the end.
- **Documentation as Code**: README, inline comments, and architecture docs are written during implementation, not after.

### 1.2 Agent Responsibilities

| Step | Owner Agent | Responsibility |
|------|-------------|----------------|
| Step 0 | @system.arch | Architecture Definition (this document) |
| Step 1 | @project.mgr | Project scaffolding, dependencies, environment setup |
| Step 2 | @frontend.eng | CLI interface, input validation, progress display |
| Step 3 | @backend.eng | CrewAI agents, tasks, workflow orchestration |
| Step 4 | @integration.eng | End-to-end workflow integration, report generation |
| Step 5 | @qa.eng | Unit tests, integration tests, quality gates |
| Step 6 | @project.mgr | Local MVP launch, documentation finalization |
| Step 7 | @project.mgr | Prepare for next phase (post-MVP planning) |

---

## 2. Build Sequence

### Step 0: Architecture Definition

**Owner:** @system.arch  
**Status:** COMPLETED  
**Deliverables:**
- System Architecture Document (sad.md)
- Architecture Plan (this document)

**Completion Criteria:**
- All 10 SAD sections filled
- All PRD requirements mapped to architectural components
- Assumptions and open questions recorded
- AAMAD_TARGET_RUNTIME documented

---

### Step 1: Environment Setup

**Owner:** @project.mgr  
**Status:** COMPLETED  
**Estimated Effort:** Day 1-2 (PRD §8.1, M1)

**Tasks:**
1. Create project directory structure per PRD §6.3:
   ```
   recruitment-assistant/
   ├── src/recruitment/
   │   ├── __init__.py
   │   ├── main.py
   │   ├── crew.py
   │   ├── config/
   │   │   ├── agents.yaml
   │   │   └── tasks.yaml
   │   └── tools/
   │       ├── __init__.py
   │       └── custom_tools.py
   ├── tests/
   ├── .env.example
   ├── .gitignore
   ├── pyproject.toml
   └── README.md
   ```

2. Initialize `pyproject.toml` with dependencies:
   - `crewai[tools]>=1.15.1`
   - `pyyaml`
   - `python-dotenv`
   - `pytest`
   - `pytest-asyncio`

3. Create `.env.example` with required variables (PRD §4.8):
   ```
   OPENAI_API_KEY=your_api_key_here           # API key for GLM-5.2 via https://api.iamhc.cn
   SERPER_API_KEY=your_serper_api_key_here
   LLM_MODEL=glm-5.2                          # Default model
   LLM_BASE_URL=https://api.iamhc.cn/v1       # OpenAI-compatible endpoint for GLM-5.2
   ```

4. Create `.gitignore` with standard Python patterns plus `.env`

5. Create `config/agents.yaml` with agent definitions (PRD §6.4)

6. Create `config/tasks.yaml` with task definitions (PRD §6.5)

7. Create `README.md` with setup instructions (PRD §5.4, NFR-004)

**Completion Criteria:**
- `uv sync` installs all dependencies without errors
- Project structure matches PRD §6.3
- `.env.example` contains all required variables
- README includes setup steps (< 15 minutes per PRD §5.4)

**Completion Date:** July 8, 2026  
**Completed By:** @project.mgr  
**Status:** ✅ COMPLETED

---

### Step 2: Frontend Development (CLI Interface)

**Owner:** @frontend.eng  
**Status:** ✅ COMPLETED  
**Start Date:** Jul 8, 2026  
**End Date:** Jul 8, 2026  
**Estimated Effort:** Day 9-10 (PRD §8.1, M4)

**Note:** Despite being assigned to @frontend.eng, this step builds the CLI interface. The web chat UI is deferred to v0.2.0 (PRD §8.2).

**Tasks Completed:**
1. ✅ Implement `src/recruitment/main.py` — Entry point (PRD §4.7, FR-007):
   - Command-line argument parsing
   - Interactive job description input via prompts
   - Validate required fields (PRD §4.2):
     - Job title (required)
     - Job description (min 100 characters)
     - Key responsibilities (min 3 items)
     - Required qualifications (min 3 items)
     - Preferred qualifications (optional)
     - Perks and benefits (optional)
   - Display progress indicators during execution (Rich library)
   - Format and display final report (Markdown rendering)
   - Save report to `candidate_report.md`

2. ✅ Implement input validation logic:
   - Reject empty or incomplete job descriptions
   - Prompt user for missing required fields
   - Display specific error messages with guidance

3. ✅ Implement progress display:
   - Agent name and current task status (Rich Status)
   - Elapsed time counter
   - Error messages with actionable guidance

4. ✅ Implement `src/recruitment/crew.py` stub:
   - Load agents from config/agents.yaml
   - Load tasks from config/tasks.yaml
   - Assemble Crew with Sequential process
   - kickoff() method that accepts job_requirements
   - Placeholder tool implementation for @backend.eng

**Deliverables:**
- `src/recruitment/main.py` - Full CLI interface
- `src/recruitment/crew.py` - Crew assembly stub
- `project-context/2.build/frontend-plan.md` - Implementation plan

**Completion Criteria Met:**
- ✅ User can run `uv run recruitment` and complete input flow
- ✅ Input validation catches all malformed inputs
- ✅ Progress is displayed during execution
- ✅ Report is displayed in terminal and saved to file
- ✅ Error messages are actionable and clear

---

### Step 3: Backend Development (CrewAI Agents & Workflow)

**Owner:** @backend.eng  
**Status:** ✅ COMPLETED  
**Start Date:** Jul 8, 2026  
**End Date:** Jul 8, 2026  
**Estimated Effort:** Day 3-8 (PRD §8.1, M2 + M3)

**Tasks Completed:**

**Phase 3a: Agent Implementation (Day 3-5, M2)**

1. ✅ Implement `src/recruitment/crew.py` — Crew assembly:
   - Load agents from `config/agents.yaml` using CrewAI Agent class
   - Load tasks from `config/tasks.yaml` using CrewAI Task class
   - Assemble Crew with Sequential process (Process.sequential)
   - Configure verbose=True, memory=True, cache=True, max_rpm=10
   - Implement `kickoff()` method with job_requirements input variable
   - Context passing: TASK-02 gets TASK-01 output, TASK-03 gets TASK-02, etc.

2. ✅ Implement agent configurations (PRD §6.4):
   - AGENT-01: Job Candidate Researcher (SerperDevTool, ScrapeWebsiteTool)
   - AGENT-02: Candidate Matcher and Scorer (SerperDevTool, ScrapeWebsiteTool)
   - AGENT-03: Candidate Outreach Strategist (SerperDevTool, ScrapeWebsiteTool)
   - AGENT-04: Candidate Reporting Specialist (no tools — synthesis only)
   - All agents: allow_delegation=False, verbose=True

3. ✅ Implement task configurations (PRD §6.5):
   - TASK-01: research_candidates_task (no context)
   - TASK-02: match_and_score_candidates_task (context: TASK-01)
   - TASK-03: outreach_strategy_task (context: TASK-02)
   - TASK-04: report_candidates_task (context: all prior tasks)

**Phase 3b: Workflow Integration (Day 6-8, M3)**

4. ✅ Implement sequential process orchestration (PRD §4.1):
   - TASK-01 → TASK-02 → TASK-03 → TASK-04
   - Context passing between agents via CrewAI Task context parameter
   - Error handling with retry and exponential backoff (PRD §5.2)

5. ✅ Implement `src/recruitment/tools/custom_tools.py`:
   - `get_tools_for_agent()` factory with graceful degradation
   - `check_tool_availability()` for SerperDevTool and ScrapeWebsiteTool
   - `retry_with_backoff()` decorator (1s, 2s, 4s, max 3 retries per PRD §5.2)
   - Legacy tool classes (CandidateSearchTool, CandidateScoringTool, OutreachTemplateTool)

6. ✅ YAML config verification:
   - All 4 agent keys match between agents.yaml and crew.py
   - All 4 task keys match between tasks.yaml and crew.py
   - Task-to-agent mapping verified
   - {job_requirements} variable interpolation verified

**Deliverables:**
- `src/recruitment/crew.py` - Full CrewAI crew assembly and orchestration
- `src/recruitment/tools/custom_tools.py` - Tool wrappers with retry logic
- `src/recruitment/tools/__init__.py` - Updated exports

**Completion Criteria Met:**
- ✅ All 4 agents load from YAML configuration with correct tools
- ✅ All 4 tasks execute in sequence with context passing
- ✅ Tool integration works with SerperDevTool and ScrapeWebsiteTool
- ✅ Error handling with exponential backoff (PRD §5.2)
- ✅ Graceful degradation when API keys are missing
- ✅ YAML config alignment verified

**Phase 3b: Workflow Integration (Day 6-8, M3)**

4. Implement sequential process orchestration (PRD §4.1):
   - TASK-01 → TASK-02 → TASK-03 → TASK-04
   - Context passing between agents
   - Error handling with retry and backoff (PRD §5.2)

5. Implement `src/recruitment/tools/custom_tools.py`:
   - Custom tool wrappers for SerperDevTool
   - Custom tool wrappers for ScrapeWebsiteTool
   - Error handling for API failures

6. Implement output generation (PRD §4.6):
   - Markdown report formatting
   - File output to `candidate_report.md`
   - Agent reasoning trace inclusion

**Completion Criteria:**
- All 4 agents load from YAML configuration
- All 4 tasks execute in sequence
- Tool integration works with SerperDev API
- Final report is generated as markdown
- Error handling catches and reports failures

---

### Step 4: Integration

**Owner:** @integration.eng  
**Status:** ✅ COMPLETED  
**Start Date:** Jul 8, 2026  
**End Date:** Jul 8, 2026  
**Estimated Effort:** Included in M3-M4

**Tasks Completed:**
1. ✅ Connect CLI input to CrewAI workflow:
   - `main.py:run_workflow()` imports `RecruitmentCrew` and calls `crew.kickoff(job_requirements)`
   - `format_job_requirements()` converts dict → formatted string
   - `crew.kickoff()` returns normalized string (handles `AgentOutput` or raw)
   - Report saved to `candidate_report.md` and displayed in terminal

2. ✅ Integration test suite created:
   - `tests/test_integration.py` — 66 tests across 14 test classes
   - All 66 integration tests pass (72 total with existing tests)
   - Covers: imports, config loading, validation, formatting, agent/task creation, crew assembly, data flow, error handling

3. ✅ Manual verification:
   - Import check: `from recruitment.main import main` ✓
   - Import check: `from recruitment.crew import RecruitmentCrew` ✓
   - Crew initialization: loads 4 agents, 4 tasks from YAML ✓
   - Full test suite: 72 passed ✓

**Deliverables:**
- `tests/test_integration.py` — Integration test suite
- `project-context/2.build/integration-notes.md` — Integration documentation

**Completion Criteria Met:**
- ✅ Complete workflow runs from CLI input to report output (verified via code inspection and test)
- ✅ Data flow validated: dict → format → string → crew.kickoff() → report string
- ✅ All YAML config alignment verified (agents, tasks, placeholders)
- ✅ Error handling validated (empty input, missing config, tool unavailability)
- ✅ No regressions in existing functionality (6 existing tests still pass)

---

### Step 5: Quality Assurance

**Owner:** @qa.eng  
**Status:** PENDING  
**Estimated Effort:** Day 11-14 (PRD §8.1, M5)

**Tasks:**

1. Unit tests (PRD §7.5, F-040):
   - Test input validation logic
   - Test agent configuration loading
   - Test task configuration loading
   - Test report formatting
   - Test error handling paths

2. Integration tests (PRD §7.5, F-041):
   - Test agent workflow execution
   - Test task dependency chain
   - Test context passing between agents
   - Test tool error handling

3. End-to-end test (PRD §7.5, F-042):
   - Run complete workflow with sample input
   - Verify report quality
   - Measure execution time

4. Performance benchmarks (PRD §7.5, F-043):
   - Benchmark each task execution time
   - Benchmark total workflow time
   - Identify bottlenecks

5. Quality gates:
   - All tests pass
   - Linting passes (ruff)
   - Type checking passes (mypy)
   - Documentation complete

**Completion Criteria:**
- Test coverage >= 80% (PRD §12.2)
- All tests pass
- No linting errors
- Performance within targets

---

### Step 6: Local MVP Launch

**Owner:** @project.mgr  
**Status:** PENDING  
**Estimated Effort:** Day 14 (PRD §8.1, M5)

**Tasks:**
1. Final README review and update
2. Verify `.env.example` completeness
3. Verify setup time < 15 minutes (PRD §5.4)
4. Run complete workflow demo
5. Capture execution logs for documentation
6. Tag v0.1.0 release (internal)

**Completion Criteria:**
- Fresh setup completes in < 15 minutes
- Workflow executes successfully with sample input
- Report is generated and formatted correctly
- All documentation is complete

---

### Step 7: Prepare for Next Phase

**Owner:** @project.mgr  
**Status:** PENDING  
**Estimated Effort:** Included in M5

**Tasks:**
1. Document post-MVP roadmap (PRD §8.2):
   - v0.2.0: Web chat UI (Next.js + assistant-ui)
   - v0.3.0: ATS integration (Greenhouse, Lever)
   - v0.4.0: Multi-role hiring support
   - v0.5.0: Analytics dashboard
   - v1.0.0: Production-ready with auth, multi-tenancy

2. Document lessons learned
3. Identify technical debt from MVP
4. Prepare AAMAD Phase 3 deliverables outline

**Completion Criteria:**
- Post-MVP roadmap documented
- Technical debt list created
- Phase 3 outline prepared

---

## 3. Status Tracking

| Step | Description | Owner | Status | Start Date | End Date | Notes |
|------|-------------|-------|--------|------------|----------|-------|
| 0 | Architecture Definition | @system.arch | COMPLETED | Jul 7, 2026 | Jul 7, 2026 | SAD and Architecture Plan created |
| 1 | Environment Setup | @project.mgr | COMPLETED | Jul 8, 2026 | Jul 8, 2026 | PRD §8.1, M1: Day 1-2 |
| 2 | Frontend Development (CLI) | @frontend.eng | COMPLETED | Jul 8, 2026 | Jul 8, 2026 | PRD §8.1, M4: Day 9-10 |
| 3 | Backend Development (CrewAI) | @backend.eng | ✅ COMPLETED | Jul 8, 2026 | Jul 8, 2026 | PRD §8.1, M2+M3: Day 3-8 |
| 4 | Integration | @integration.eng | ✅ COMPLETED | Jul 8, 2026 | Jul 8, 2026 | PRD §8.1, M3-M4 |
| 5 | Quality Assurance | @qa.eng | PENDING | — | — | PRD §8.1, M5: Day 11-14 |
| 6 | Local MVP Launch | @project.mgr | PENDING | — | — | PRD §8.1, M5: Day 14 |
| 7 | Prepare for Next Phase | @project.mgr | PENDING | — | — | PRD §8.1, M5: Day 14 |

---

## 4. Dependencies and Risks

### 4.1 Technical Dependencies

| Dependency | Type | Required For | Risk Level | Source |
|------------|------|--------------|------------|--------|
| Python >=3.10 | Runtime | All steps | Low | PRD §6.2 |
| uv package manager | Tool | Step 1 | Low | PRD §6.2 |
| CrewAI >=1.15.1 | Framework | Step 3 | Medium | PRD §9.1 |
| GLM-5.2 API (via https://api.iamhc.cn) | External API (OpenAI-compatible) | Step 3 | Medium | PRD §9.1 |
| Serper.dev API | External API | Step 3 | Medium | PRD §9.1 |

### 4.2 Technical Risks

| Risk | Impact | Likelihood | Mitigation | Owner | Source |
|------|--------|------------|------------|-------|--------|
| LLM API rate limits | Workflow delays | Medium | Implement retry with exponential backoff | @backend.eng | PRD §11 |
| Serper.dev API costs | Budget overrun | Medium | Monitor usage, implement caching | @project.mgr | PRD §11 |
| Agent hallucination | Inaccurate candidates | Medium | Structured output validation | @qa.eng | PRD §11 |
| Tool failures | Incomplete reports | Medium | Graceful degradation, fallback | @backend.eng | PRD §11 |
| Scope creep | MVP delay | High | Strict adherence to PRD scope | @product-mgr | PRD §11 |
| CrewAI API changes | Build failures | Low | Pin dependency versions | @backend.eng | — |
| Python version incompatibility | Setup failures | Low | Test on Python 3.10, 3.11, 3.12 | @qa.eng | — |

### 4.3 Risk Mitigation Strategies

1. **API Rate Limits**: Exponential backoff (1s, 2s, 4s, max 3 retries) per PRD §5.2
2. **API Costs**: Cache LLM responses, limit search queries per execution
3. **Agent Hallucination**: Validate outputs against expected schemas, include confidence levels
4. **Tool Failures**: Continue with available data, note limitations in output
5. **Scope Creep**: Reference PRD §2.1 for every feature decision; defer anything not in scope

---

## 5. Milestone Timeline

**2-Week Sprint** (PRD §8.1)

| Milestone | Days | Deliverables | Owner | Dependencies |
|-----------|------|--------------|-------|--------------|
| M1: Project Setup | 1-2 | Scaffolding, dependencies, configuration | @project.mgr | None |
| M2: Agent Implementation | 3-5 | 4 agents with tools, YAML configs | @backend.eng | M1 |
| M3: Workflow Integration | 6-8 | Sequential process, input/output flow | @backend.eng, @integration.eng | M2 |
| M4: CLI Interface | 9-10 | User input, progress display, report output | @frontend.eng | M3 |
| M5: Testing & Polish | 11-14 | Tests, documentation, bug fixes | @qa.eng, @project.mgr | M4 |

### Timeline Visualization

```
Week 1:                          Week 2:
Day 1  Day 2  Day 3  Day 4  Day 5  Day 6  Day 7  Day 8  Day 9  Day 10 Day 11 Day 12 Day 13 Day 14
|------|------|------|------|------|------|------|------|------|------|------|------|------|------|
[M1: Project Setup    ]
       [M2: Agent Implementation          ]
                               [M3: Workflow Integration          ]
                                                 [M4: CLI Interface     ]
                                                               [M5: Testing & Polish                   ]
```

---

## Assumptions

1. **AAMAD_TARGET_RUNTIME = crewai**: CrewAI is the primary runtime framework.
2. **2-week sprint**: MVP delivery within 14 calendar days.
3. **Local execution only**: No cloud deployment, containerization, or CI/CD for MVP.
4. **CLI-first**: Web UI deferred to v0.2.0.
5. **Sequential execution**: Steps must be completed in order; no parallel work.
6. **API availability**: The GLM-5.2 endpoint (https://api.iamhc.cn, OpenAI-compatible) and Serper.dev API are accessible during development.
7. **Single developer**: Each step is owned by one agent; no multi-agent parallelism.

---

## Open Questions

1. **Build Order**: Should Step 2 (CLI) and Step 3 (Backend) be swapped?
   - *Recommendation*: Implement Step 3 first (backend), then Step 2 (CLI), as the CLI depends on the backend being functional.
   - *Decision*: Follow PRD §8.1 ordering (M2 before M4).

2. **Test-Driven Development**: Should tests be written before or alongside implementation?
   - *Recommendation*: Write tests alongside implementation for each feature.
   - *Decision*: Tests are part of each step, not a separate phase.

3. **Documentation Timing**: Should documentation be written during or after implementation?
   - *Recommendation*: Write documentation during implementation.
   - *Decision*: README and inline docs are part of each step.

---

*This Architecture Plan guides the execution of AAMAD Phase 2. Each step will be executed by the assigned agent following the build sequence.*
