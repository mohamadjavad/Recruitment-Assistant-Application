"use client";

import {
  AssistantRuntimeProvider,
  useLocalRuntime,
  ThreadPrimitive,
  MessagePrimitive,
  MessagePartPrimitive,
  ComposerPrimitive,
  type ChatModelAdapter,
} from "@assistant-ui/react";
import { JobDescriptionForm } from "@/components/job-description-form";
import { AgentStatusPanel } from "@/components/agent-status-panel";

export default function HomePage() {
  const runtime = useLocalRuntime(
    // ChatModelAdapter stub — frontend engineer will wire /api/chat SSE stream
    chatModelAdapterStub,
  );

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-8rem)]">
        {/* Left sidebar: JD input + Agent Status */}
        <aside className="lg:col-span-1 flex flex-col gap-4 overflow-y-auto">
          <JobDescriptionForm />
          <AgentStatusPanel />
        </aside>

        {/* Main chat area */}
        <section className="lg:col-span-2 border border-border rounded-lg overflow-hidden bg-white flex flex-col">
          {/* Messages area */}
          <div className="flex-1 overflow-y-auto p-4">
            <ThreadPrimitive.Root className="h-full">
              <ThreadPrimitive.Viewport className="space-y-4">
                <ThreadPrimitive.Empty>
                  <div className="text-center text-muted-foreground py-12">
                    <p className="text-lg font-medium">
                      Welcome to Recruitment Assistant
                    </p>
                    <p className="text-sm mt-2">
                      I can help you find and evaluate candidates for your open
                      positions. Paste a job description or use the form on the
                      left to get started.
                    </p>
                  </div>
                </ThreadPrimitive.Empty>
                <ThreadPrimitive.Messages>
                  {() => (
                    <MessagePrimitive.Root>
                      <div className="py-2">
                        <MessagePrimitive.Parts>
                          {({ part }) => {
                            if (part.type === "text") {
                              return (
                                <p style={{ whiteSpace: "pre-line" }} className="text-sm">
                                  {part.text}
                                </p>
                              );
                            }
                            return null;
                          }}
                        </MessagePrimitive.Parts>
                      </div>
                    </MessagePrimitive.Root>
                  )}
                </ThreadPrimitive.Messages>
              </ThreadPrimitive.Viewport>
              <ThreadPrimitive.ScrollToBottom />
            </ThreadPrimitive.Root>
          </div>

          {/* Composer input */}
          <div className="border-t border-border p-3">
            <ComposerPrimitive.Root>
              <ComposerPrimitive.Input
                className="w-full px-3 py-2 text-sm border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                placeholder="Enter a job description or ask a question..."
              />
              <div className="flex justify-end mt-2">
                <ComposerPrimitive.Send className="bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium py-1.5 px-4 rounded-md transition-colors">
                  Send
                </ComposerPrimitive.Send>
              </div>
            </ComposerPrimitive.Root>
          </div>
        </section>
      </div>
    </AssistantRuntimeProvider>
  );
}

// ── Stub ChatModelAdapter ────────────────────────────────────
// Frontend engineer: Replace with SSE-based streaming adapter
// that POSTs to /api/chat and reads SSE events.
// See src/lib/sse-client.ts for the SSE client wrapper.

const chatModelAdapterStub: ChatModelAdapter = {
  async run({ abortSignal }) {
    const text = [
      "Starting recruitment workflow...",
      "",
      "**Researcher**: Searching for candidates...",
      "- Found 12 potential candidates on LinkedIn",
      "- Scraped 8 candidate profiles from GitHub",
      "",
      "**Matcher**: Scoring candidates...",
      "- Top candidate: Jane Doe (score: 92/100)",
      "",
      "**Report ready!** Check the agent status panel for details.",
    ].join("\n");

    // Simulate async work
    await new Promise((r) => setTimeout(r, 500));

    if (abortSignal?.aborted) {
      return { content: [] };
    }

    return {
      content: [{ type: "text" as const, text }],
    };
  },
};

