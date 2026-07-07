# Recruitment Assistant

Open-source, multi-agent recruitment assistant built on CrewAI. Automates candidate sourcing, evaluation, outreach strategy, and recruiter reporting.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement and Value Proposition](#problem-statement-and-value-proposition)
- [Key Features](#key-features)
- [Application Architecture](#application-architecture)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Next Steps for Contributors](#next-steps-for-contributors)
- [License](#license)

---

## Project Overview

The Recruitment Assistant is an open-source, multi-agent system that leverages CrewAI's autonomous agent orchestration to automate the recruitment workflow. The system accepts a job description and produces a comprehensive candidate report through a pipeline of four specialized AI agents: a Researcher, a Matcher, a Communicator, and a Reporter.

The project targets a 50% reduction in time-to-fill while maintaining transparency, auditability, and compliance. Candidate data remains local by default, and every agent decision is explainable.

**References:**
- PRD section 1.1 — Vision Statement
- MRD section 1 — Executive Summary

---

## Problem Statement and Value Proposition

### The Problem

Manual recruitment is slow, expensive, and inefficient:

- **Time-to-fill exceeds 40 days** for technical roles on average, creating competitive disadvantage in tight labor markets (MRD section 2.2, Key Market Drivers).
- **Bad hires cost 30% of first-year salary**, with downstream impacts on team productivity and morale (MRD section 2.2).
- **60-70% of recruiter time is consumed by sourcing**, leaving little capacity for relationship building and strategic hiring (MRD section 3.1, Pain Points).
- **Outreach response rates average 10-15%**, indicating widespread inefficiency in candidate engagement strategies.

### The Value Proposition

| Benefit | Description |
|---------|-------------|
| 50% reduction in time-to-fill | Multi-agent parallel research and automated outreach compress the hiring timeline |
| Transparent AI decision-making | Every agent decision is logged with reasoning traces for auditability |
| Open-source extensibility | MIT-licensed, YAML-configurable, tool-pluggable architecture |
| Privacy by design | Support for local LLM deployment (Ollama, LM Studio); no candidate data leaves your infrastructure by default |

**References:**
- PRD section 1.3 — Product Principles
- MRD section 2.2 — Key Market Drivers
- MRD section 3.1 — Primary Target Pain Points

---

## Key Features

The MVP delivers a chat-based recruitment assistant with the following capabilities (PRD section 2.1):

- **4-agent sequential workflow** — Researcher, Matcher, Communicator, and Reporter agents execute in sequence, each building on the previous agent's output
- **Job description input** — Accept job requirements via chat interface in natural language or structured format
- **Candidate research** — Web search and scraping tools discover qualified candidates from public sources
- **Candidate scoring and ranking** — Each candidate is scored 0-100 against job requirements with transparent justification across five weighted dimensions (skills match, experience, education, location, additional factors)
- **Outreach strategy generation** — Personalized outreach templates including initial contact, follow-up sequence, and interview invitation
- **Recruiter-ready report output** — Comprehensive markdown report with candidate profiles, scores, outreach strategies, and methodology
- **YAML configuration** — Agent roles, goals, backstories, and task definitions are configured via `agents.yaml` and `tasks.yaml`
- **LLM flexibility** — Supports OpenAI GPT-4o (default) and local LLM alternatives via LiteLLM-compatible providers

**Out of scope for MVP:** ATS integration, LinkedIn direct integration, multi-role hiring, analytics dashboard, user authentication, candidate database, email sending, video interview scheduling, mobile application.

---

## Application Architecture

The system executes a 4-agent sequential workflow when a job description is provided (PRD section 4.1).

### Agent Pipeline

```
Job Description
      |
      v
+-------------------+
| AGENT-01          |
| Job Candidate     |    Tools: SerperDevTool, ScrapeWebsiteTool
| Researcher        |    Output: 10+ candidate profiles
+-------------------+
      |
      v
+-------------------+
| AGENT-02          |
| Candidate Matcher |    Tools: SerperDevTool, ScrapeWebsiteTool
| and Scorer        |    Output: Ranked candidates with scores
+-------------------+
      |
      v
+-------------------+
| AGENT-03          |
| Candidate Outreach|    Tools: SerperDevTool, ScrapeWebsiteTool
| Strategist        |    Output: Outreach strategies and templates
+-------------------+
      |
      v
+-------------------+
| AGENT-04          |
| Candidate         |    Tools: None (synthesis only)
| Reporting Specialist|   Output: Final comprehensive report
+-------------------+
      |
      v
candidate_report.md
```

### Task Flow (PRD section 6.1)

| Task | Agent | Input | Output |
|------|-------|-------|--------|
| TASK-01 | AGENT-01: Researcher | Job requirements | List of 10+ candidate profiles with contact info and brief summaries |
| TASK-02 | AGENT-02: Matcher | Job requirements + TASK-01 output | Ranked candidate list with scores and justifications |
| TASK-03 | AGENT-03: Communicator | Job requirements + TASK-02 output | Outreach strategies, templates, and engagement tactics |
| TASK-04 | AGENT-04: Reporter | All previous task outputs | Final recruiter-ready report in markdown |

### Scoring Dimensions (PRD section 4.4)

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Skills Match | 40% | Required skills present in profile |
| Experience Level | 25% | Years and relevance of experience |
| Education | 15% | Degree and field of study |
| Location | 10% | Geographic match to job location |
| Additional Factors | 10% | Certifications, publications, awards |

---

## Getting Started

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | >= 3.10, < 3.14 | Required by CrewAI |
| uv | Latest | Package manager (recommended over pip) |
| OpenAI API key | — | Required if using GPT-4o (default LLM) |
| Serper.dev API key | — | Required for web search capability |

For local LLM usage, install Ollama or LM Studio as an alternative to OpenAI.

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-org/recruitment-assistant.git
   cd recruitment-assistant
   ```

2. **Install dependencies:**

   ```bash
   uv sync
   ```

3. **Configure environment variables:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set the required API keys:

   ```
   OPENAI_API_KEY=your-openai-api-key
   SERPER_API_KEY=your-serper-api-key
   ```

   For local LLM usage, set:

   ```
   LLM_BASE_URL=http://localhost:11434
   LLM_MODEL=ollama/llama3
   ```

4. **Verify configuration:**

   Review `src/recruitment/config/agents.yaml` and `src/recruitment/config/tasks.yaml` to confirm agent and task definitions match your requirements.

### Running the Application

```bash
uv run recruitment
```

The system will:

1. Prompt for job description input via the CLI
2. Execute the 4-agent sequential workflow
3. Generate `candidate_report.md` in the project root

Expected execution time: under 5 minutes for a complete workflow run.

---

## Project Structure

```
recruitment-assistant/
├── .env.example                    # Environment variable template
├── .gitignore
├── pyproject.toml                  # Project dependencies
├── README.md                       # This file
├── src/recruitment/
│   ├── __init__.py
│   ├── main.py                     # Entry point and CLI
│   ├── crew.py                     # Crew assembly and orchestration
│   ├── config/
│   │   ├── agents.yaml             # Agent definitions (roles, goals, backstories)
│   │   └── tasks.yaml              # Task definitions (descriptions, expected outputs)
│   └── tools/
│       ├── __init__.py
│       └── custom_tools.py         # Custom tool implementations
├── project-context/                # AAMAD artifacts
│   ├── 1.define/
│   │   ├── mrd.md                  # Market Research Document
│   │   └── prd.md                  # Product Requirements Document
│   ├── 2.build/
│   └── 3.deliver/
└── tests/                          # Test suite (Phase 2)
```

**References:**
- PRD section 6.3 — Project Structure

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes (if using OpenAI) | — | OpenAI API key |
| `SERPER_API_KEY` | Yes | — | Serper.dev API key |
| `LLM_MODEL` | No | `gpt-4o` | LLM model identifier |
| `LLM_BASE_URL` | No | — | Custom LLM endpoint (Ollama, LM Studio) |
| `LI_AT` | No | — | LinkedIn session cookie (demo only) |

### Agent Configuration (`agents.yaml`)

Agent roles, goals, and backstories are defined in `src/recruitment/config/agents.yaml`. Each agent entry follows this schema:

```yaml
agent_name:
  role: "Human-readable role title"
  goal: "One-sentence objective"
  backstory: "2-3 sentence background"
```

### Task Configuration (`tasks.yaml`)

Task descriptions and expected outputs are defined in `src/recruitment/config/tasks.yaml`. Tasks support `{variable}` interpolation for dynamic input.

**References:**
- PRD section 4.8 — Configuration Management
- PRD section 6.4 — Agent Configuration
- PRD section 6.5 — Task Configuration

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Runtime Framework | CrewAI | >= 1.15.1 |
| Language | Python | >= 3.10, < 3.14 |
| Dependency Manager | uv | Latest |
| LLM Provider | OpenAI (GPT-4o) | Default |
| LLM Alternative | Ollama / LM Studio | Supported |
| Web Search | SerperDevTool | Via crewai_tools |
| Web Scraping | ScrapeWebsiteTool | Via crewai_tools |
| Configuration | YAML | PyYAML |

**References:**
- PRD section 6.2 — Technology Stack
- PRD section 9.1 — External Dependencies

---

## Next Steps for Contributors

### Current Status

Phase 1 (Define) is complete. The Market Research Document (MRD) and Product Requirements Document (PRD) have been finalized and are available in `project-context/1.define/`.

### What Comes Next

Phase 2 (Build) follows the AAMAD workflow:

1. **Step 0 — Architecture Definition** (`@system.arch`): Generate the System Architecture Document (SAD) at `project-context/2.build/sad.md`
2. **Step 1 — Environment Setup** (`@project.mgr`): Scaffold project directories, install dependencies, configure environment
3. **Step 2 — Frontend Development** (`@frontend.eng`): Implement the MVP chat interface
4. **Step 3 — Backend Development** (`@backend.eng`): Build the CrewAI backend with agent orchestration
5. **Step 4 — Integration** (`@integration.eng`): Wire frontend to backend API
6. **Step 5 — Quality Assurance** (`@qa.eng`): Validate MVP functionality end-to-end
7. **Step 6 — Local MVP Launch**: Run the complete workflow locally

### How to Contribute

1. **Review the PRD** at `project-context/1.define/prd.md` to understand the full scope and requirements
2. **Set the runtime target** in your environment:
   ```
   AAMAD_TARGET_RUNTIME=crewai
   ```
3. **Follow the AAMAD workflow** as defined in `CHECKLIST.md` — each phase has designated agent personas
4. **Consult agent definitions** in `AGENTS.md` for role-specific instructions
5. **Check the checklist** in `CHECKLIST.md` for the complete execution sequence

### Agent Personas

| Persona | Role | Responsibility |
|---------|------|----------------|
| `@product-mgr` | Product Manager | Orchestrates product vision and requirements |
| `@system.arch` | System Architect | Produces SAD and SFS documents |
| `@project.mgr` | Project Manager | Scaffolds project and environment |
| `@frontend.eng` | Frontend Developer | Builds MVP chat interface |
| `@backend.eng` | Backend Developer | Builds CrewAI backend |
| `@integration.eng` | Integration Engineer | Connects frontend and backend |
| `@qa.eng` | QA Engineer | Validates MVP functionality |

### Release Plan

| Version | Features | Target |
|---------|----------|--------|
| v0.1.0 | MVP — Core workflow, CLI interface, 4 agents, report output | 2 weeks |
| v0.2.0 | Web chat UI (Next.js + assistant-ui) | Month 2 |
| v0.3.0 | ATS integration (Greenhouse, Lever) | Month 3 |
| v0.4.0 | Multi-role hiring support | Month 4 |
| v0.5.0 | Analytics dashboard | Month 5 |
| v1.0.0 | Production-ready with auth, multi-tenancy | Month 6 |

**References:**
- PRD section 8 — Release Plan
- CHECKLIST.md — AAMAD Execution Checklist
- AGENTS.md — Agent Framework Definitions

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

*Built with the AAMAD (Agentic AI Multi-Agent Development) framework. Powered by CrewAI.*
