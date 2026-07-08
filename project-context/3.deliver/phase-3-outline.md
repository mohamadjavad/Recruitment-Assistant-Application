# Phase 3 Outline — Post-MVP Development

**Date:** July 8, 2026  
**Prepared by:** @product-mgr  
**Source:** PRD §8.2, MRD §4, SAD §10.4, QA sign-off

---

## 1. Priority Order

| Priority | Version | Feature | Effort | Dependencies |
|----------|---------|---------|--------|--------------|
| **P0** | v0.2.0 | Web Chat UI (Next.js + assistant-ui) | 5-10 days | SAD §3.4 architecture is ready |
| **P1** | v0.2.1 | Fix QA-01/02/04 — polish pass | 2-3 days | None |
| **P2** | v0.3.0 | ATS Integration (Greenhouse, Lever) | 10-15 days | API partnerships, OAuth |
| **P3** | v0.4.0 | Multi-Role Hiring + Hierarchical Process | 5-8 days | v0.2.0 for UI foundation |
| **P4** | v0.5.0 | Analytics Dashboard | 8-10 days | Database (SQLite) |
| **P5** | v1.0.0 | Auth, Multi-Tenancy, Production | 10-15 days | v0.5.0 analytics |

---

## 2. v0.2.0 — Web Chat UI (Immediate Next Step)

### Objective
Convert the CLI tool into a recruiter-friendly web application.

### Architecture (from SAD §3.4)
| Component | Technology |
|-----------|------------|
| Framework | Next.js App Router |
| UI Library | assistant-ui + shadcn/ui |
| Styling | Tailwind CSS |
| Streaming | Server-Sent Events (SSE) |
| Integration | Next.js API routes → Python CrewAI service |

### Key Deliverables
1. Chat interface with streaming agent responses
2. Job description input form (structured → natural language)
3. Real-time progress display via SSE (fixes QA-01)
4. Interactive setup wizard (fixes QA-02)
5. GitHub Actions CI with ruff + mypy + pytest

### Effort Breakdown
| Task | Days |
|------|------|
| Next.js project scaffolding + Tailwind + assistant-ui | 1 |
| API route: proxy to CrewAI with SSE streaming | 2 |
| Chat UI: message list, input, agent status indicator | 2 |
| Input form: job description collection | 1 |
| Polish: error states, loading, responsive design | 1 |
| CI/CD: GitHub Actions + .env setup wizard | 1 |
| Integration test + manual QA | 1 |
| **Total** | **~9 days** |

---

## 3. v0.3.0 — ATS Integration

### Target Systems
- Greenhouse (highest demand per MRD §4)
- Lever (second priority)
- Workday (enterprise, complex integration)

### Scope
- Inbound: Pull job descriptions from ATS
- Outbound: Push candidate reports and outreach templates
- OAuth 2.0 authentication flow

---

## 4. v0.4.0 — Multi-Role & Hierarchical Process

### Features
- Support multiple simultaneous job descriptions
- Hierarchical CrewAI process with manager agent
- Replace sequential 4-agent pipeline
- Parallel task execution where possible
- Expected to reduce E2E time below 5 min target

---

## 5. v0.5.0 — Analytics & Database

### Features
- SQLite database for persistent storage
- Time-to-fill tracking
- Candidate pipeline metrics
- Execution history and audit log
- Basic dashboard (if web UI exists)

---

## 6. v1.0.0 — Production Readiness

### Features
- Multi-tenancy with user authentication (Clerk/Auth0)
- Docker containerization
- Kubernetes deployment manifests
- GDPR/EEOC compliance audit
- Performance benchmarks and load testing
- Enterprise SSO

---

## 7. Cross-Cutting Concerns

| Concern | When to Address |
|---------|-----------------|
| CI/CD Pipeline (GitHub Actions) | v0.2.0 |
| Database Migration (SQLite → scalable) | v0.5.0 |
| LLM Provider Switching (LiteLLM) | v0.2.0 (web UI config) |
| API Rate Limiting / Caching | v0.2.0 (SSE streaming) |
| Security Audit | v1.0.0 |
| Documentation Site | v0.2.0 |

---

*This outline serves as the reference for AAMAD Phase 3 planning. Priorities are based on user impact, competitive positioning (MRD §4), and technical dependency order.*
