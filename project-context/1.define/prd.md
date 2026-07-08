# Product Requirements Document (PRD)

## Recruitment Assistant Application — CrewAI Multi-Agent System

**Document Version:** 1.0  
**Date:** July 7, 2026  
**Prepared by:** @product-mgr (AAMAD Phase 1 — Define)  
**Input Source:** project-context/1.define/mrd.md

---

## 1. Product Vision

### 1.1 Vision Statement

Build an open-source, multi-agent recruitment assistant that automates candidate sourcing, evaluation, outreach strategy, and recruiter reporting — leveraging CrewAI's autonomous agent orchestration to reduce time-to-fill by 50% while maintaining transparency and compliance.

### 1.2 Mission

Deliver a production-ready MVP that demonstrates the power of multi-agent collaboration in recruitment, built on CrewAI's proven reference architecture, with a clean chat-based interface and extensible agent framework.

### 1.3 Product Principles

1. **Agent-First Architecture**: Every feature is implemented as an agent or task, not hardcoded logic.
2. **Transparency Over Speed**: Every agent decision is explainable and auditable.
3. **Human in the Loop**: AI recommends; humans decide. No autonomous candidate contact.
4. **Open & Extensible**: MIT-licensed, YAML-configurable, tool-pluggable.
5. **Privacy by Design**: Support local LLM deployment; no candidate data leaves the user's infrastructure by default.

---

## 2. Product Scope

### 2.1 MVP Definition

The MVP is a **chat-based recruitment assistant** that accepts a job description and produces a comprehensive candidate report through a multi-agent workflow.

**In Scope (MVP):**

- 4-agent sequential workflow (Researcher, Matcher, Communicator, Reporter)
- Job description input via chat interface
- Candidate research using web search and scraping
- Candidate scoring and ranking against job requirements
- Outreach strategy and template generation
- Final recruiter-ready report output
- Configuration via YAML files
- Support for GLM-5.2 (via OpenAI-compatible endpoint) and local LLM alternatives

**Out of Scope (MVP):**

- ATS integration (Greenhouse, Lever, Workday)
- LinkedIn direct integration (compliance risk)
- Multi-role hiring (multiple job descriptions simultaneously)
- Analytics dashboard
- User authentication and multi-tenancy
- Candidate database / CRM
- Email sending / outreach automation
- Video interview scheduling
- Mobile application

### 2.2 MVP Success Criteria

| Criterion                | Target                   | Measurement                     |
| ------------------------ | ------------------------ | ------------------------------- |
| Time to Complete         | < 5 minutes              | End-to-end workflow execution   |
| Candidate Report Quality | 10+ qualified candidates | Recruiter review score >= 3.5/5 |
| Outreach Response Rate   | 20%+ improvement         | Compared to manual outreach     |
| Time-to-Fill Reduction   | 30%+ reduction           | Compared to pre-tool baseline   |
| User Satisfaction        | NPS >= 40                | Post-MVP survey                 |

---

## 3. User Stories

### 3.1 Primary User Stories

#### US-01: Input Job Requirements

**As a** Talent Acquisition VP  
**I want to** input a job description through a chat interface  
**So that** the system can begin the automated recruitment workflow

**Acceptance Criteria:**

- User can paste a job description in natural language or structured format
- System parses and validates job requirements (title, description, requirements, qualifications)
- System confirms receipt and begins workflow execution
- Error handling for malformed or incomplete job descriptions

#### US-02: Research Candidates

**As a** recruiter  
**I want the** Researcher agent to find 10+ qualified candidates  
**So that** I have a diverse pool of potential hires to evaluate

**Acceptance Criteria:**

- Researcher agent searches web sources for matching candidates
- Results include name, role, location, and brief profile
- Candidates meet minimum job requirements
- Source URLs are provided for verification
- Output is structured and reproducible

#### US-03: Score and Rank Candidates

**As a** recruiter  
**I want the** Matcher agent to score candidates against job requirements  
**So that** I can prioritize outreach to the best-fit candidates

**Acceptance Criteria:**

- Each candidate receives a score (1-100) with justification
- Scoring considers: skills match, experience level, location, education
- Candidates are ranked from highest to lowest score
- Scoring methodology is transparent and auditable

#### US-04: Generate Outreach Strategy

**As a** recruiter  
**I want the** Communicator agent to create outreach templates  
**So that** I can engage candidates with personalized, professional messaging

**Acceptance Criteria:**

- Outreach templates are customizable per candidate tier
- Templates include: initial contact, follow-up, and interview invitation
- Tone and messaging align with employer brand
- Templates are ready for immediate use

#### US-05: View Final Report

**As a** recruiter  
**I want to** receive a comprehensive candidate report  
**So that** I can make informed hiring decisions and share with hiring managers

**Acceptance Criteria:**

- Report includes: candidate profiles, scores, outreach strategies, summary
- Report is formatted as markdown for easy sharing
- Report is saved to a file for archival
- Report includes agent reasoning traces for auditability

### 3.2 Secondary User Stories

#### US-06: Configure Agent Parameters

**As a** technical administrator  
**I want to** modify agent roles, goals, and tools via YAML  
**So that** the system can be customized for different industries and roles

**Acceptance Criteria:**

- Agent configurations are in `config/agents.yaml`
- Task configurations are in `config/tasks.yaml`
- Changes take effect on next workflow execution
- Documentation explains configuration options

#### US-07: Switch LLM Provider

**As a** technical administrator  
**I want to** switch between OpenAI and local LLMs  
**So that** I can optimize for cost, privacy, or performance

**Acceptance Criteria:**

- LLM configuration is in `.env` or `crew.py`
- Support for OpenAI, Ollama, LM Studio, and other LiteLLM-compatible providers
- Fallback mechanism if primary LLM is unavailable
- Performance benchmarks for each provider

---

## 4. Functional Requirements

### 4.1 Core Workflow (FR-001)

**Description:** The system shall execute a 4-agent sequential workflow when a job description is provided.

**Agents:**

| Agent ID | Role                           | Goal                                           | Tools                            |
| -------- | ------------------------------ | ---------------------------------------------- | -------------------------------- |
| AGENT-01 | Job Candidate Researcher       | Find potential candidates via web search       | SerperDevTool, ScrapeWebsiteTool |
| AGENT-02 | Candidate Matcher and Scorer   | Score and rank candidates against requirements | SerperDevTool, ScrapeWebsiteTool |
| AGENT-03 | Candidate Outreach Strategist  | Develop engagement strategies and templates    | SerperDevTool, ScrapeWebsiteTool |
| AGENT-04 | Candidate Reporting Specialist | Compile recruiter-ready final report           | None (synthesis only)            |

**Tasks:**

| Task ID | Agent    | Input                             | Output                            |
| ------- | -------- | --------------------------------- | --------------------------------- |
| TASK-01 | AGENT-01 | Job requirements                  | List of 10+ candidate profiles    |
| TASK-02 | AGENT-02 | Job requirements + TASK-01 output | Ranked candidate list with scores |
| TASK-03 | AGENT-03 | Job requirements + TASK-02 output | Outreach strategies and templates |
| TASK-04 | AGENT-04 | All previous task outputs         | Final comprehensive report        |

**Process:** Sequential (TASK-01 → TASK-02 → TASK-03 → TASK-04)

### 4.2 Job Description Input (FR-002)

**Description:** The system shall accept job descriptions in structured or natural language format.

**Required Fields:**

- Job title
- Job description (minimum 100 characters)
- Key responsibilities (minimum 3 items)
- Required qualifications (minimum 3 items)
- Preferred qualifications (optional)
- Perks and benefits (optional)

**Input Validation:**

- Reject empty or incomplete job descriptions
- Prompt user for missing required fields
- Accept both YAML-formatted and natural language input

### 4.3 Candidate Research (FR-003)

**Description:** The Researcher agent shall search for qualified candidates using available web tools.

**Search Strategy:**

- Use SerperDevTool for web search queries
- Use ScrapeWebsiteTool to extract candidate information from profiles
- Target professional networks, company websites, and public profiles
- Collect: name, current role, location, skills summary, profile URL

**Quality Requirements:**

- Minimum 10 candidates per search
- No duplicate candidates
- Candidates must meet minimum 3 of 5 required qualifications
- Source URLs must be valid and accessible

### 4.4 Candidate Scoring (FR-004)

**Description:** The Matcher agent shall evaluate and score each candidate against job requirements.

**Scoring Dimensions:**

| Dimension          | Weight | Scoring Criteria                     |
| ------------------ | ------ | ------------------------------------ |
| Skills Match       | 40%    | Required skills present in profile   |
| Experience Level   | 25%    | Years and relevance of experience    |
| Education          | 15%    | Degree and field of study            |
| Location           | 10%    | Geographic match to job location     |
| Additional Factors | 10%    | Certifications, publications, awards |

**Scoring Output:**

- Overall score: 0-100
- Dimension scores with justification
- Confidence level (high/medium/low)
- Rank order from highest to lowest score

### 4.5 Outreach Strategy (FR-005)

**Description:** The Communicator agent shall develop personalized outreach strategies for top candidates.

**Output Components:**

- Initial contact email/message template
- Follow-up sequence (2-3 messages)
- Interview invitation template
- Personalization tokens for each candidate
- Recommended outreach channel (email, LinkedIn, etc.)

**Template Requirements:**

- Professional tone aligned with employer brand
- Mobile-friendly formatting
- Clear call-to-action
- Compliance with anti-spam regulations

### 4.6 Final Report (FR-006)

**Description:** The Reporter agent shall compile a comprehensive recruiter-ready report.

**Report Structure:**

```markdown
# Candidate Report: [Job Title]

## Executive Summary

- Total candidates found: [N]
- Top candidates: [N]
- Recommended next steps

## Candidate Profiles

### 1. [Candidate Name] — Score: [N/100]

- Current Role
- Location
- Key Skills
- Experience Summary
- Score Justification
- Outreach Strategy

### 2. [Candidate Name] — Score: [N/100]

...

## Outreach Templates

### Initial Contact

### Follow-up Sequence

### Interview Invitation

## Methodology

- Research approach
- Scoring criteria
- Agent reasoning traces
```

**Output Format:** Markdown file saved to project root as `candidate_report.md`

### 4.7 Chat Interface (FR-007)

**Description:** The system shall provide a chat-based interface for user interaction.

**MVP Interface:**

- Command-line interface for input/output
- Structured prompts for job description input
- Progress indicators during agent execution
- Formatted report display upon completion

**Future Interface (Post-MVP):**

- Web-based chat UI (Next.js + assistant-ui)
- Real-time agent progress streaming
- Interactive report viewing and export
- Multi-session management

### 4.8 Configuration Management (FR-008)

**Description:** The system shall be configurable via YAML files and environment variables.

**Configuration Files:**

- `config/agents.yaml` — Agent roles, goals, backstories
- `config/tasks.yaml` — Task descriptions, expected outputs
- `.env` — API keys, LLM settings, tool configurations
- `crew.py` — Crew assembly, process type, verbose settings

**Environment Variables:**

| Variable       | Required                             | Default              | Description                                                         |
| -------------- | ------------------------------------ | -------------------- | ------------------------------------------------------------------- |
| OPENAI_API_KEY | Yes (if using OpenAI-compatible API) | —                    | API key for OpenAI-compatible endpoint (e.g., https://api.iamhc.cn) |
| SERPER_API_KEY | Yes                                  | —                    | Serper.dev API key                                                  |
| LI_AT          | No                                   | —                    | LinkedIn session cookie (demo only)                                 |
| LLM_MODEL      | No                                   | glm-5.2              | LLM model identifier                                                |
| LLM_BASE_URL   | No                                   | https://api.iamhc.cn | Custom LLM endpoint (OpenAI-compatible, Ollama, etc.)               |

---

## 5. Non-Functional Requirements

### 5.1 Performance (NFR-001)

| Metric                      | Target                |
| --------------------------- | --------------------- |
| End-to-end execution time   | < 5 minutes           |
| Agent task completion time  | < 90 seconds per task |
| Concurrent workflow support | 1 user (MVP)          |
| Report generation time      | < 30 seconds          |

### 5.2 Reliability (NFR-002)

| Metric                   | Target                            |
| ------------------------ | --------------------------------- |
| Workflow completion rate | >= 95%                            |
| Agent error recovery     | Graceful fallback on tool failure |
| LLM timeout handling     | Retry with exponential backoff    |
| Data validation          | Schema validation on all outputs  |

### 5.3 Security (NFR-003)

| Requirement             | Implementation                             |
| ----------------------- | ------------------------------------------ |
| API key storage         | Environment variables, never in code       |
| Candidate data handling | Local processing only, no external storage |
| LLM data privacy        | Support local LLM deployment               |
| Audit trail             | Agent reasoning traces logged              |

### 5.4 Usability (NFR-004)

| Requirement    | Implementation                             |
| -------------- | ------------------------------------------ |
| Setup time     | < 15 minutes for technical users           |
| Learning curve | < 30 minutes to first workflow run         |
| Error messages | Clear, actionable guidance                 |
| Documentation  | README, inline comments, architecture docs |

### 5.5 Extensibility (NFR-005)

| Requirement    | Implementation                  |
| -------------- | ------------------------------- |
| Tool addition  | Custom tools via Python classes |
| Agent addition | YAML config + Python decorator  |
| LLM switching  | LiteLLM-compatible providers    |
| Output formats | Configurable output files       |

---

## 6. Technical Architecture

### 6.1 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│                  (CLI / Web Chat)                         │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  CrewAI Runtime                          │
│            (Sequential Process Manager)                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │Researcher│→ │ Matcher  │→ │Communi-  │→ │ Reporter ││
│  │  Agent   │  │  Agent   │  │cator     │  │  Agent   ││
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘│
│       │              │              │              │      │
│  ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐       │      │
│  │SerperDev │  │SerperDev │  │SerperDev │       │      │
│  │ScrapeWeb │  │ScrapeWeb │  │ScrapeWeb │       │      │
│  └──────────┘  └──────────┘  └──────────┘       │      │
│                                                  │      │
└──────────────────────────────────────────────────┼──────┘
                                                   │
                                                   ▼
                                          ┌──────────────┐
                                          │candidate_    │
                                          │report.md     │
                                          └──────────────┘
```

### 6.2 Technology Stack

| Component          | Technology                               | Version          |
| ------------------ | ---------------------------------------- | ---------------- |
| Runtime Framework  | CrewAI                                   | >=1.15.1         |
| Language           | Python                                   | >=3.10, <3.14    |
| Dependency Manager | uv                                       | Latest           |
| LLM Provider       | GLM-5.2 (via OpenAI-compatible endpoint) | Default          |
| LLM Alternative    | Ollama / LM Studio                       | Supported        |
| Web Search         | SerperDevTool                            | Via crewai_tools |
| Web Scraping       | ScrapeWebsiteTool                        | Via crewai_tools |
| Configuration      | YAML                                     | PyYAML           |
| Package Manager    | uv / poetry                              | uv preferred     |

### 6.3 Project Structure

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
└── tests/                          # Test suite (Phase 2)
```

### 6.4 Agent Configuration (agents.yaml)

```yaml
researcher:
  role: >
    Job Candidate Researcher
  goal: >
    Find potential candidates for the job
  backstory: >
    You are adept at finding the right candidates by exploring various online
    resources. Your skill in identifying suitable candidates ensures the best
    match for job positions.

matcher:
  role: >
    Candidate Matcher and Scorer
  goal: >
    Match the candidates to the best jobs and score them
  backstory: >
    You have a knack for matching the right candidates to the right job positions
    using advanced algorithms and scoring techniques. Your scores help
    prioritize the best candidates for outreach.

communicator:
  role: >
    Candidate Outreach Strategist
  goal: >
    Develop outreach strategies for the selected candidates
  backstory: >
    You are skilled at creating effective outreach strategies and templates to
    engage candidates. Your communication tactics ensure high response rates
    from potential candidates.

reporter:
  role: >
    Candidate Reporting Specialist
  goal: >
    Report the best candidates to the recruiters
  backstory: >
    You are proficient at compiling and presenting detailed reports for recruiters.
    Your reports provide clear insights into the best candidates to pursue.
```

### 6.5 Task Configuration (tasks.yaml)

````yaml
research_candidates_task:
  description: >
    Conduct thorough research to find potential candidates for the specified job.
    Utilize various online resources and databases to gather a comprehensive list
    of potential candidates. Ensure that the candidates meet the job requirements
    provided.

    Job Requirements:
    {job_requirements}
  expected_output: >
    A list of 10 potential candidates with their contact information and brief
    profiles highlighting their suitability.

match_and_score_candidates_task:
  description: >
    Evaluate and match the candidates to the best job positions based on their
    qualifications and suitability. Score each candidate to reflect their
    alignment with the job requirements, ensuring a fair and transparent
    assessment process.

    Job Requirements:
    {job_requirements}
  expected_output: >
    A ranked list of candidates with detailed scores and justifications for each
    job position.

outreach_strategy_task:
  description: >
    Develop a comprehensive strategy to reach out to the selected candidates.
    Create effective outreach methods and templates that can engage the candidates
    and encourage them to consider the job opportunity.

    Job Requirements:
    {job_requirements}
  expected_output: >
    A detailed list of outreach methods and templates ready for implementation,
    including communication strategies and engagement tactics.

report_candidates_task:
  description: >
    Compile a comprehensive report for recruiters on the best candidates to put
    forward. Summarize the findings from the previous tasks and provide clear
    recommendations based on the job requirements.
  expected_output: >
    A detailed report with the best candidates to pursue, including profiles,
    scores, and outreach strategies. Formatted as markdown without '```'.
````

---

## 7. Epics and Features

### 7.1 Epic 1: Core Workflow Engine

| Feature ID | Feature                          | Priority | Effort |
| ---------- | -------------------------------- | -------- | ------ |
| F-001      | CrewAI project scaffolding       | P0       | 2 days |
| F-002      | Agent configuration (4 agents)   | P0       | 1 day  |
| F-003      | Task configuration (4 tasks)     | P0       | 1 day  |
| F-004      | Sequential process orchestration | P0       | 1 day  |
| F-005      | Input validation and parsing     | P0       | 1 day  |
| F-006      | Output file generation           | P0       | 1 day  |

### 7.2 Epic 2: Agent Tools

| Feature ID | Feature                       | Priority | Effort   |
| ---------- | ----------------------------- | -------- | -------- |
| F-010      | SerperDevTool integration     | P0       | 0.5 days |
| F-011      | ScrapeWebsiteTool integration | P0       | 0.5 days |
| F-012      | Custom tool framework         | P1       | 1 day    |
| F-013      | Tool error handling           | P1       | 0.5 days |

### 7.3 Epic 3: User Interface

| Feature ID | Feature                   | Priority | Effort   |
| ---------- | ------------------------- | -------- | -------- |
| F-020      | CLI input interface       | P0       | 1 day    |
| F-021      | Progress indicators       | P1       | 0.5 days |
| F-022      | Report display formatting | P1       | 0.5 days |
| F-023      | Web chat UI (Next.js)     | P1       | 5 days   |

### 7.4 Epic 4: Configuration & Deployment

| Feature ID | Feature                         | Priority | Effort   |
| ---------- | ------------------------------- | -------- | -------- |
| F-030      | YAML configuration system       | P0       | 0.5 days |
| F-031      | Environment variable management | P0       | 0.5 days |
| F-032      | LLM provider switching          | P1       | 1 day    |
| F-033      | Docker containerization         | P2       | 1 day    |

### 7.5 Epic 5: Quality & Testing

| Feature ID | Feature                        | Priority | Effort   |
| ---------- | ------------------------------ | -------- | -------- |
| F-040      | Unit tests for tools           | P1       | 1 day    |
| F-041      | Integration tests for workflow | P1       | 1 day    |
| F-042      | End-to-end workflow test       | P1       | 1 day    |
| F-043      | Performance benchmarks         | P2       | 0.5 days |

---

## 8. Release Plan

### 8.1 MVP Release (v0.1.0)

**Target Date:** 2 weeks from project start  
**Scope:** Core workflow, CLI interface, 4 agents, report output

**Milestones:**

| Milestone                | Duration  | Deliverables                                |
| ------------------------ | --------- | ------------------------------------------- |
| M1: Project Setup        | Day 1-2   | Scaffolding, dependencies, configuration    |
| M2: Agent Implementation | Day 3-5   | 4 agents with tools, YAML configs           |
| M3: Workflow Integration | Day 6-8   | Sequential process, input/output flow       |
| M4: CLI Interface        | Day 9-10  | User input, progress display, report output |
| M5: Testing & Polish     | Day 11-14 | Tests, documentation, bug fixes             |

### 8.2 Post-MVP Releases

| Version | Features                                  | Target  |
| ------- | ----------------------------------------- | ------- |
| v0.2.0  | Web chat UI (Next.js + assistant-ui)      | Month 2 |
| v0.3.0  | ATS integration (Greenhouse, Lever)       | Month 3 |
| v0.4.0  | Multi-role hiring support                 | Month 4 |
| v0.5.0  | Analytics dashboard                       | Month 5 |
| v1.0.0  | Production-ready with auth, multi-tenancy | Month 6 |

---

## 9. Dependencies

### 9.1 External Dependencies

| Dependency                      | Type       | Version          | Notes               |
| ------------------------------- | ---------- | ---------------- | ------------------- |
| CrewAI                          | Framework  | >=1.15.1         | Core orchestration  |
| GLM-5.2 (OpenAI-compatible API) | LLM        | glm-5.2          | Default model       |
| Serper.dev                      | Web Search | API key required | Free tier available |
| Python                          | Runtime    | >=3.10, <3.14    | Required by CrewAI  |

### 9.2 Internal Dependencies

| Dependency          | Source           | Notes                    |
| ------------------- | ---------------- | ------------------------ |
| AAMAD Framework     | project-context/ | Phase 1 artifacts        |
| System Architecture | @system.arch     | SAD document (Phase 2)   |
| Frontend UI         | @frontend.eng    | Chat interface (Phase 2) |
| Backend API         | @backend.eng     | CrewAI backend (Phase 2) |

---

## 10. Assumptions

1. **AAMAD_TARGET_RUNTIME = crewai**: The system will use CrewAI as the primary runtime.
2. **MVP is CLI-first**: Web UI is deferred to post-MVP to reduce scope.
3. **Single-user MVP**: Multi-tenancy and authentication are post-MVP features.
4. **GLM-5.2 default**: Users must have access to the GLM-5.2 API endpoint (https://api.iamhc.cn) or configure an alternative LLM.
5. **Serper.dev required**: Web search is essential for candidate research.
6. **No LinkedIn scraping**: Production use of LinkedIn scraping violates ToS; MVP uses compliant sources only.
7. **Sequential process**: Hierarchical process with manager agent is deferred to post-MVP.

---

## 11. Risks

| Risk                 | Impact                | Mitigation                       | Owner        |
| -------------------- | --------------------- | -------------------------------- | ------------ |
| LLM API rate limits  | Workflow delays       | Implement retry with backoff     | @backend.eng |
| Serper.dev API costs | Budget overrun        | Monitor usage, implement caching | @project.mgr |
| Agent hallucination  | Inaccurate candidates | Structured output validation     | @qa.eng      |
| Tool failures        | Incomplete reports    | Graceful degradation, fallback   | @backend.eng |
| Scope creep          | MVP delay             | Strict adherence to PRD scope    | @product-mgr |

---

## 12. Success Metrics

### 12.1 Product Metrics

| Metric                   | MVP Target  | Measurement                  |
| ------------------------ | ----------- | ---------------------------- |
| Workflow completion rate | >= 95%      | Successful runs / total runs |
| Report generation time   | < 5 minutes | Average end-to-end time      |
| Candidate quality score  | >= 3.5/5    | Recruiter review rating      |
| User satisfaction (NPS)  | >= 40       | Post-usage survey            |
| Time-to-fill reduction   | >= 30%      | Comred to baseline           |

### 12.2 Technical Metrics

| Metric                     | Target       | Measurement                |
| -------------------------- | ------------ | -------------------------- |
| Test coverage              | >= 80%       | Unit + integration tests   |
| Documentation completeness | 100%         | All features documented    |
| Setup time                 | < 15 minutes | First-time user onboarding |
| Error rate                 | < 5%         | Failed workflow runs       |

---

## 13. Open Questions

1. **Web UI Priority**: Should the web chat UI be included in MVP or deferred?
   - _Recommendation:_ Defer to v0.2.0; MVP focuses on CLI workflow.

2. **LLM Model Selection**: Should we support multiple LLM providers in MVP or focus on GLM-5.2?
   - _Recommendation:_ Support GLM-5.2 (OpenAI-compatible) + Ollama in MVP; extend to other providers post-MVP.

3. **Compliance Requirements**: What level of GDPR/EEOC compliance is required for MVP?
   - _Recommendation:_ Document compliance gaps; address in v0.3.0+.

4. **Pricing Model**: Should the MVP be free/open-source or include a commercial tier?
   - _Recommendation:_ Free/open-source; commercial features in enterprise tier.

---

## 14. Appendicespa

### Appendix A: CrewAI Reference

- **Repository:** https://github.com/crewAIInc/crewAI
- **Documentation:** https://docs.crewai.com
- **Recruitment Example:** https://github.com/crewAIInc/crewAI-examples/tree/main/crews/recruitment
- **License:** MIT

### Appendix B: AAMAD Framework

- **Runtime:** crewai (AAMAD_TARGET_RUNTIME)
- **Phase:** 1 — Define (MRD + PRD)
- **Next Phase:** 2 — Build (SAD + Implementation)
- **Artifacts:** project-context/1.define/

### Appendix C: Agent Configuration Reference

```yaml
# Agent configuration schema
agent_name:
  role: "Human-readable role title"
  goal: "One-sentence objective"
  backstory: "2-3 sentence background"
  tools: [ToolClass1, ToolClass2]
  allow_delegation: false
  verbose: true
```

### Appendix D: Task Configuration Reference

```yaml
# Task configuration schema
task_name:
  description: >
    Multi-line task description with {variable} interpolation.
    Include context from previous tasks as needed.
  expected_output: >
    Clear description of expected output format and content.
  agent: agent_name
  output_file: optional_output.md
```

---

_This PRD defines the MVP scope for the Recruitment Assistant application. Technical implementation details will be defined in the System Architecture Document (SAD) during AAMAD Phase 2._
