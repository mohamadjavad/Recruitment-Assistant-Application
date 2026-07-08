import { NextRequest } from "next/server";
import { spawn } from "child_process";
import path from "path";
import { existsSync } from "fs";

/**
 * POST /api/chat
 *
 * SSE streaming endpoint that:
 * 1. Receives job description JSON
 * 2. Writes it to a temp file
 * 3. Spawns `uv run python scripts/run_recruitment_sse.py --sse --input <tmpfile>`
 * 4. Pipes stdout lines as SSE events
 *
 * This is a STUB — the frontend/backend engineers will wire the real subprocess
 * spawning and SSE parsing logic.
 *
 * Architecture per SAD v2 §3.3.2:
 *   Browser ←SSE← Next.js API Route ←subprocess← Python CrewAI
 */

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { job_requirements } = body;

    if (!job_requirements) {
      return new Response(
        JSON.stringify({ error: "Missing job_requirements in request body" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    // ── Stub: Return a canned SSE stream ──────────────────────
    // Replace this with real subprocess spawning:
    //
    // 1. Write job_requirements to a temp JSON file
    // 2. Spawn: uv run python scripts/run_recruitment_sse.py --sse --input <tmpfile>
    // 3. Read stdout line-by-line, parse JSON, emit SSE events
    // 4. On client disconnect (request.signal.aborted), kill subprocess
    // 5. Clean up temp file
    //
    // See src/lib/sse-client.ts for the browser-side EventSource wrapper.
    // See scripts/run_recruitment_sse.py for the SSE protocol.

    const stream = new ReadableStream({
      start(controller) {
        const encoder = new TextEncoder();

        const emit = (event: string, data: object) => {
          controller.enqueue(
            encoder.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`)
          );
        };

        // Simulated SSE events (replace with real subprocess output)
        const emitSimulated = async () => {
          emit("agent_start", {
            agent: "Researcher",
            task: "TASK-01",
            description: "Searching for candidates...",
            timestamp: new Date().toISOString(),
          });
          await sleep(500);
          emit("agent_progress", {
            agent: "Researcher",
            progress: 50,
            message: "Scanning LinkedIn profiles...",
          });
          await sleep(500);
          emit("agent_complete", {
            agent: "Researcher",
            output: "Found 12 candidates",
            duration_seconds: 1.2,
          });
          await sleep(300);
          emit("agent_start", {
            agent: "Matcher",
            task: "TASK-02",
            description: "Scoring and ranking candidates...",
            timestamp: new Date().toISOString(),
          });
          await sleep(700);
          emit("agent_complete", {
            agent: "Matcher",
            output: "Scored 12 candidates",
            duration_seconds: 0.8,
          });
          await sleep(300);
          emit("report_ready", {
            report_path: "candidate_report.md",
            size_bytes: 45678,
            duration_total: 3.5,
          });
          emit("workflow_complete", {
            status: "success",
            candidates_found: 12,
            avg_score: 85.4,
          });
          controller.close();
        };

        emitSimulated().catch((err) => {
          emit("error", {
            code: "STREAM_ERROR",
            message: err instanceof Error ? err.message : String(err),
            severity: "error",
          });
          controller.close();
        });
      },
    });

    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  } catch (error) {
    return new Response(
      JSON.stringify({
        error: "Failed to process request",
        details: error instanceof Error ? error.message : String(error),
      }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
