import { NextRequest } from "next/server";

/**
 * GET /api/chat/status
 *
 * Returns the current workflow execution status.
 *
 * This is a STUB — the backend engineer will wire this to track
 * the state of the subprocess spawned by the POST /api/chat endpoint.
 *
 * Response:
 *   { status: "idle" | "running" | "complete" | "error", elapsed_seconds: number }
 */

type WorkflowStatus = "idle" | "running" | "complete" | "error";

// In-memory workflow state (replace with proper state management)
let currentStatus: WorkflowStatus = "idle";
let startTime: number | null = null;

export async function GET(request: NextRequest) {
  const elapsed = startTime ? Math.floor((Date.now() - startTime) / 1000) : 0;

  return new Response(
    JSON.stringify({
      status: currentStatus,
      elapsed_seconds: elapsed,
      message: getStatusMessage(currentStatus),
    }),
    {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }
  );
}

function getStatusMessage(status: WorkflowStatus): string {
  switch (status) {
    case "idle":
      return "No workflow running. Submit a job description to start.";
    case "running":
      return "Workflow is executing. Agents are processing...";
    case "complete":
      return "Workflow completed successfully. Report is ready.";
    case "error":
      return "Workflow encountered an error. Check logs for details.";
  }
}

// ── Exported for the POST handler to update state ──────────
export function setWorkflowStatus(status: WorkflowStatus) {
  currentStatus = status;
  if (status === "running") {
    startTime = Date.now();
  }
  if (status === "idle") {
    startTime = null;
  }
}
