# Technical Debt — MVP v0.1.0

**Date:** July 8, 2026  
**Source:** QA sign-off and @product-mgr review

---

## 1. Known Issues

| ID | Issue | Area | Severity | Status |
|----|-------|------|----------|--------|
| QA-01 | Progress display disconnected from real agent execution | `main.py:373-379` | Medium | Open |
| QA-02 | No .env file in project — fresh clones need manual copy | `main.py:409-419` | Medium | Open |
| QA-03 | 453 CrewAI deprecation warnings per test run | CrewAI internals | Minor | Monitor |
| QA-04 | RecruitmentCrew initialized twice per workflow | `main.py:354, 379` | Minor | Open |

---

## 2. Design Trade-offs Accepted

| Decision | Rationale | When to Revisit |
|----------|-----------|-----------------|
| CLI-first (no web UI) | MVP speed — 2-week sprint constraint | v0.2.0 |
| Sequential process (4 agents) | Simpler than hierarchical for MVP | v0.4.0 |
| No database (file-based output) | Avoid infrastructure complexity | v0.5.0 (analytics) |
| No authentication / single-user | Unnecessary for local CLI tool | v1.0.0 |
| No ATS integration | Out of scope for MVP | v0.3.0 |
| No CI/CD pipeline | Local development only | v0.2.0 |
| No HTTP API layer | Not needed for CLI-only MVP | v0.2.0 (web UI) |

---

## 3. Performance Debt

| Metric | Target | Actual | Gap |
|--------|--------|--------|-----|
| E2E execution time | < 5 min (PRD §2.2) | 9m 1s | ~4m over |

**Contributing factors:**
- Sequential 4-agent workflow (total time = sum of all LLM calls)
- Full report generation in single LLM pass
- GLM-5.2 API latency

**Planned mitigations:**
- Hierarchical process with parallel tasks (v0.4.0)
- SSE streaming for perceived speed (v0.2.0)
- LLM response caching

---

## 4. Testing Debt

| Gap | Impact | Plan |
|-----|--------|------|
| No CI-enforced linting (ruff) | Code style may drift | Add GitHub Actions in v0.2.0 |
| No type checking (mypy) | Type errors may slip through | Add to same CI workflow |
| No coverage reporting (pytest-cov) | Can't verify exact 80% target | Add to CI or dev script |
| No mocked-LLM E2E test | E2E requires real API keys | Add mock-based E2E test |
| No LLM connectivity smoke test | API issues caught only at runtime | Add optional connectivity test |

---

## 5. Documentation Debt

| Gap | Plan |
|-----|------|
| LLM provider config (OPENAI_BASE_URL /v1 suffix) | Mention in .env.example comments |
| Web UI deferred architecture (SAD §3.4) | Already documented — keep current |
| ATS integration patterns | Create design doc before v0.3.0 |

---

*This document tracks deferred work and accepted trade-offs from the v0.1.0 MVP. Each item links to a planned resolution version in the phase-3-outline.*
