# v0.2.0 — Web Chat UI Project Setup

**Date:** July 8, 2026  
**Agent:** @project-mgr  
**Status:** Scaffold complete — ready for implementation agents  

---

## Overview

This scaffold implements **v0.2.0 (Web Chat UI)** as defined in SAD v2 §3. The Next.js application is placed alongside the existing Python CLI backend (recruitment-assistant/) in a Strangler Fig pattern — no existing Python files were modified.

## Files Created

### Root-level

| File | Purpose |
|------|---------|
| `.env.example` | Environment variable template with all required keys (OPENAI_API_KEY, SERPER_API_KEY, GLM_API_KEY, GLM_BASE_URL, NEXT_PUBLIC_APP_URL, LLM_MODEL, etc.) |
| `.gitignore` | Updated with Node.js / Next.js entries (node_modules/, .next/, etc.) |

### `scripts/`

| File | Purpose | Status |
|------|---------|--------|
| `run_recruitment_sse.py` | SSE-aware CLI wrapper for RecruitmentCrew. Emits structured JSON events to stdout. Supports `--sse`, `--input`, `--check-env` flags. | ✅ Importable (`uv run python ../scripts/run_recruitment_sse.py --help` works) |
| `upgrade.py` | QA-04 reference script — lazy-init singleton pattern for RecruitmentCrew. Does **not** modify existing files. | ✅ Works |

### `.github/workflows/`

| File | Purpose |
|------|---------|
| `ci.yml` | GitHub Actions CI — Python: ruff, mypy, pytest. Node: npm ci, lint, tsc, build. SSE wrapper check. |

### `nextjs-app/`

#### Config files

| File | Purpose |
|------|---------|
| `package.json` | Dependencies: next@16, react@19, @assistant-ui/react@0.14, @assistant-ui/react-ai-sdk@1.3, zustand@5, tailwindcss@4, typescript@6 |
| `tsconfig.json` | TypeScript config with `@/*` path alias, bundler module resolution |
| `next.config.ts` | Next.js config with increased body size limit |
| `postcss.config.mjs` | PostCSS with `@tailwindcss/postcss` (Tailwind v4) |
| `tailwind.config.ts` | Tailwind config with custom primary color palette |
| `.gitignore` | Node-specific ignores |

#### Source files

| File | Purpose | Status |
|------|---------|--------|
| `src/app/globals.css` | `@import "tailwindcss"` + base styles + assistant-ui overrides | ✅ |
| `src/app/layout.tsx` | Root layout with header and container | ✅ |
| `src/app/page.tsx` | Main chat page with assistant-ui primitives (ThreadPrimitive, MessagePrimitive, ComposerPrimitive) + stub ChatModelAdapter | ✅ |
| `src/app/api/chat/route.ts` | POST /api/chat — SSE streaming endpoint. **Stub**: returns simulated SSE events | ⚠️ Stub |
| `src/app/api/chat/status/route.ts` | GET /api/chat/status — workflow status check | ⚠️ Stub |
| `src/app/api/setup/check/route.ts` | GET /api/setup/check — environment configuration check | ⚠️ Stub |
| `src/app/api/setup/validate/route.ts` | POST /api/setup/validate — API key validation | ⚠️ Stub |
| `src/components/job-description-form.tsx` | Structured JD input form with validation | ⚠️ Stub |
| `src/components/agent-status-panel.tsx` | Real-time agent progress panel with SSE integration placeholder | ⚠️ Stub |
| `src/components/setup-wizard.tsx` | First-launch wizard with API key/test connection UI | ⚠️ Stub |
| `src/lib/store.ts` | Zustand store for chat state, SSE event handling, agent status | ⚠️ Stub |
| `src/lib/sse-client.ts` | EventSource wrapper for SSE consumption | ⚠️ Stub |

**Key**: ✅ = functional, ⚠️ = placeholder/stub for engineers to implement

## Verification Results

### 1. `cd nextjs-app && npm install`
```
added 476 packages — ✅ No peer dep errors
```

### 2. `npx tsc --noEmit`
```
✅ Compiled with zero TypeScript errors
```

### 3. `uv run python ../scripts/run_recruitment_sse.py --help`
```
✅ Help text displays correctly — wrapper is importable and functional
```

### 4. `uv run python ../scripts/upgrade.py --help`
```
✅ Help text displays correctly
```

## Architecture Decisions

1. **Strangler Fig**: All v0.2.0 files are **new additions**. No existing Python files in `recruitment-assistant/` were modified.

2. **assistant-ui API version**: Using `@assistant-ui/react@0.14.x` (latest). The API uses:
   - `useLocalRuntime(chatModelAdapter)` — first arg is ChatModelAdapter (not options object)
   - `ThreadPrimitive`, `MessagePrimitive`, `MessagePartPrimitive`, `ComposerPrimitive` — composable primitives
   - `ExternalThread` — controlled thread component (available but not used in stub)
   - Render function pattern: `<ThreadPrimitive.Messages>{() => <MessagePrimitive.Root>...</>}</ThreadPrimitive.Messages>`

3. **SSE Protocol**: Python → stdout JSON lines → Next.js API route parses → browser receives SSE `event:` + `data:` lines via `EventSource` (or fetch-based reader).

4. **Tailwind CSS v4**: Uses `@import "tailwindcss"` syntax (not `@tailwind` directives). PostCSS plugin `@tailwindcss/postcss`.

## Next Steps for Implementation Agents

### @frontend.eng — Frontend Engineer

1. **Wire `page.tsx` ChatModelAdapter** to POST to `/api/chat` and consume SSE stream
2. **Implement `sse-client.ts`** — real fetch() SSE parsing with reconnection logic
3. **Implement `store.ts`** — connect Zustand store to SSE events
4. **Implement `job-description-form.tsx`** — wire form submission to trigger workflow
5. **Implement `agent-status-panel.tsx`** — real-time agent progress from SSE events
6. **Implement `setup-wizard.tsx`** — API key validation flow using `/api/setup/*`
7. **Style refinement** — polish the chat UI, responsive layout, dark mode
8. **Component tests** — add unit tests for components

### @backend.eng — Backend Engineer

1. **Implement `/api/chat/route.ts`** — real subprocess spawning:
   ```typescript
   const proc = spawn("uv", ["run", "python", "../scripts/run_recruitment_sse.py", "--sse", "--input", tmpfile]);
   ```
   - Write job_requirements to temp JSON file
   - Read stdout line-by-line, parse JSON, emit SSE events
   - Handle client disconnect with `proc.kill()`
   - Clean up temp files

2. **Implement `/api/chat/status/route.ts`** — track workflow state in memory/Redis
3. **Implement `/api/setup/check/route.ts`** — read `.env` file to check config
4. **Implement `/api/setup/validate/route.ts`** — test API key against LLM provider
5. **Implement `run_recruitment_sse.py`** — replace simulated agent progress with real CrewAI callbacks (the SSE wrapper currently has `time.sleep(0.3)` placeholders for the 4 agents; replace with actual `crew.kickoff()` with proper event emission)
6. **Implement `upgrade.py`** — integrate singleton pattern into `main.py` (QA-04)
7. **Add test coverage** — tests for the SSE wrapper, API routes (mocked subprocess)

### @integration.eng — Integration Engineer

1. **End-to-end flow**: Verify that POST `/api/chat` → subprocess spawn → SSE stream → browser receives events
2. **Error handling**: Test subprocess failure, cleanup on disconnect, temp file cleanup
3. **CI pipeline**: Verify GitHub Actions workflow runs for both Python and Node

### @qa.eng — QA Engineer

1. **Verify QA-01 fix**: Real SSE streaming replaces simulated spinner
2. **Verify QA-02 fix**: Setup wizard detects missing env vars and guides configuration
3. **Verify QA-03**: No deprecation warnings from CrewAI in SSE wrapper output
4. **Verify QA-04**: Single RecruitmentCrew initialization via subprocess
5. **Regression**: CLI still works via `uv run recruitment`
