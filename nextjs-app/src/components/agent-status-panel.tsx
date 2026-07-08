"use client";

import { useState, useEffect } from "react";

/**
 * AgentStatusPanel — Real-time agent progress display.
 *
 * Shows the current state of each agent in the recruitment workflow:
 * - Agent name and role
 * - Current task description
 * - Progress indicator (spinner or percentage)
 * - Status: idle | running | complete | error
 *
 * This is a STUB — the frontend engineer will wire this to consume
 * SSE events from /api/chat and update via Zustand store.
 *
 * SAD v2 §3.3.3: "Real-time agent state from CrewAI process.
 * Python emits structured JSON events at each agent lifecycle transition."
 */

interface AgentStatus {
  name: string;
  task: string;
  status: "idle" | "running" | "complete" | "error";
  progress: number; // 0–100
  message?: string;
}

const INITIAL_AGENTS: AgentStatus[] = [
  { name: "Researcher", task: "TASK-01", status: "idle", progress: 0, message: "Waiting..." },
  { name: "Matcher", task: "TASK-02", status: "idle", progress: 0, message: "Waiting..." },
  { name: "Communicator", task: "TASK-03", status: "idle", progress: 0, message: "Waiting..." },
  { name: "Reporter", task: "TASK-04", status: "idle", progress: 0, message: "Waiting..." },
];

export function AgentStatusPanel() {
  const [agents] = useState<AgentStatus[]>(INITIAL_AGENTS);
  const [workflowStatus, setWorkflowStatus] = useState<"idle" | "running" | "complete" | "error">("idle");

  // ── Stub: Simulate agent progress updates ────────────────
  // Replace with EventSource subscription to /api/chat SSE stream.
  // See src/lib/sse-client.ts for the SSE client wrapper.
  useEffect(() => {
    // Placeholder for SSE consumption
    // const cleanup = subscribeToSSE((event) => {
    //   // Update agent status based on event type
    //   // updateAgentStatus(event);
    // });
    // return cleanup;
  }, []);

  const statusColors: Record<string, string> = {
    idle: "bg-gray-200 text-gray-600",
    running: "bg-blue-100 text-blue-700 animate-pulse",
    complete: "bg-green-100 text-green-700",
    error: "bg-red-100 text-red-700",
  };

  return (
    <div className="bg-white border border-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-foreground">Agent Progress</h2>
        <span
          className={`text-xs font-medium px-2 py-0.5 rounded-full ${
            workflowStatus === "running" ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-600"
          }`}
        >
          {workflowStatus === "idle" ? "Idle" : workflowStatus === "running" ? "Running..." : workflowStatus}
        </span>
      </div>

      <div className="space-y-3">
        {agents.map((agent) => (
          <div key={agent.name} className="flex items-start gap-3">
            {/* Status indicator */}
            <span
              className={`inline-block w-2 h-2 mt-1.5 rounded-full ${
                agent.status === "running"
                  ? "bg-blue-500"
                  : agent.status === "complete"
                  ? "bg-green-500"
                  : agent.status === "error"
                  ? "bg-red-500"
                  : "bg-gray-300"
              }`}
            />

            {/* Agent details */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-foreground">{agent.name}</span>
                <span
                  className={`text-[10px] font-medium px-1.5 py-0.5 rounded-full ${statusColors[agent.status]}`}
                >
                  {agent.status}
                </span>
              </div>
              <p className="text-xs text-muted-foreground truncate">{agent.task}</p>
              {agent.message && (
                <p className="text-xs text-muted-foreground mt-0.5">{agent.message}</p>
              )}

              {/* Progress bar */}
              <div className="w-full bg-gray-100 rounded-full h-1.5 mt-1">
                <div
                  className={`h-1.5 rounded-full transition-all duration-500 ${
                    agent.status === "complete"
                      ? "bg-green-500"
                      : agent.status === "error"
                      ? "bg-red-500"
                      : "bg-blue-500"
                  }`}
                  style={{ width: `${agent.progress}%` }}
                />
              </div>
            </div>

            {/* Progress percentage */}
            <span className="text-xs text-muted-foreground font-mono w-8 text-right">
              {agent.progress}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
