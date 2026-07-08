"use client";

import { useState, useEffect } from "react";

/**
 * SetupWizard — First-launch configuration wizard.
 *
 * Fixes QA-02 (qa-plan.md §5.2, §7.1):
 * Detects missing API keys and guides the user through configuration.
 *
 * Steps:
 *   1. Welcome screen
 *   2. LLM provider selection
 *   3. API key input
 *   4. Test connection
 *   5. Auto-generate .env file
 *
 * This is a STUB — the frontend engineer will wire this to the
 * /api/setup/check and /api/setup/validate endpoints.
 *
 * SAD v2 §3.3.4: "Interactive setup wizard with API key validation
 * and test connection button."
 */

interface SetupState {
  step: number;
  configured: boolean | null;
  missingKeys: string[];
  provider: string;
  apiKey: string;
  baseUrl: string;
  validating: boolean;
  validationResult: { valid: boolean; message: string } | null;
}

export function SetupWizard() {
  const [state, setState] = useState<SetupState>({
    step: 0,
    configured: null,
    missingKeys: [],
    provider: "glm-5.2",
    apiKey: "",
    baseUrl: "https://api.iamhc.cn",
    validating: false,
    validationResult: null,
  });

  // Check configuration on mount
  useEffect(() => {
    fetch("/api/setup/check")
      .then((res) => res.json())
      .then((data) => {
        setState((prev) => ({
          ...prev,
          configured: data.configured,
          missingKeys: data.missing_keys || [],
          step: data.configured ? 4 : 0,
        }));
      })
      .catch(() => {
        setState((prev) => ({ ...prev, configured: false }));
      });
  }, []);

  // Don't show if configured (or still loading)
  if (state.configured === null) {
    return (
      <div className="bg-white border border-border rounded-lg p-4 text-center text-sm text-muted-foreground">
        Checking configuration...
      </div>
    );
  }

  if (state.configured) {
    return null; // Everything is configured — hide wizard
  }

  const handleValidate = async () => {
    setState((prev) => ({ ...prev, validating: true, validationResult: null }));
    try {
      const res = await fetch("/api/setup/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          provider: state.provider,
          api_key: state.apiKey,
          base_url: state.baseUrl,
        }),
      });
      const data = await res.json();
      setState((prev) => ({
        ...prev,
        validating: false,
        validationResult: data,
        step: data.valid ? 4 : prev.step,
      }));
    } catch {
      setState((prev) => ({
        ...prev,
        validating: false,
        validationResult: { valid: false, message: "Connection failed" },
      }));
    }
  };

  return (
    <div className="bg-white border border-border rounded-lg p-6 max-w-md mx-auto">
      {/* Step indicator */}
      <div className="flex gap-2 mb-6">
        {[0, 1, 2, 3, 4].map((s) => (
          <div
            key={s}
            className={`flex-1 h-1 rounded-full ${
              s <= state.step ? "bg-primary-500" : "bg-gray-200"
            }`}
          />
        ))}
      </div>

      {state.step === 0 && (
        <div className="text-center space-y-4">
          <h2 className="text-lg font-semibold">Welcome!</h2>
          <p className="text-sm text-muted-foreground">
            Let&apos;s set up your Recruitment Assistant. You&apos;ll need API keys for the LLM
            provider and web search.
          </p>
          <p className="text-xs text-muted-foreground">
            Missing keys: {state.missingKeys.join(", ") || "None detected"}
          </p>
          <button
            onClick={() => setState((prev) => ({ ...prev, step: 1 }))}
            className="bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium py-2 px-6 rounded-md transition-colors"
          >
            Get Started
          </button>
        </div>
      )}

      {state.step === 1 && (
        <div className="space-y-4">
          <h2 className="text-sm font-semibold">Select LLM Provider</h2>
          <div className="space-y-2">
            {[
              { id: "glm-5.2", label: "GLM-5.2 (Recommended)", url: "https://api.iamhc.cn" },
              { id: "openai", label: "OpenAI (GPT-4/GPT-4o)", url: "https://api.openai.com/v1" },
              { id: "ollama", label: "Ollama (Local)", url: "http://localhost:11434/v1" },
              { id: "custom", label: "Custom Endpoint", url: "" },
            ].map((p) => (
              <button
                key={p.id}
                onClick={() =>
                  setState((prev) => ({
                    ...prev,
                    provider: p.id,
                    baseUrl: p.url || prev.baseUrl,
                    step: 2,
                  }))
                }
                className="w-full text-left px-4 py-3 text-sm border border-border rounded-md hover:border-primary-500 hover:bg-primary-50 transition-colors"
              >
                <span className="font-medium">{p.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {state.step === 2 && (
        <div className="space-y-4">
          <h2 className="text-sm font-semibold">API Key</h2>
          <p className="text-xs text-muted-foreground">
            Provider: <strong>{state.provider}</strong>
          </p>
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1">
              API Key
            </label>
            <input
              type="password"
              value={state.apiKey}
              onChange={(e) => setState((prev) => ({ ...prev, apiKey: e.target.value }))}
              placeholder="sk-..."
              className="w-full px-3 py-2 text-sm border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1">
              Base URL
            </label>
            <input
              type="text"
              value={state.baseUrl}
              onChange={(e) => setState((prev) => ({ ...prev, baseUrl: e.target.value }))}
              placeholder="https://api.iamhc.cn"
              className="w-full px-3 py-2 text-sm border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <button
            onClick={() => setState((prev) => ({ ...prev, step: 3 }))}
            className="w-full bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium py-2 px-4 rounded-md transition-colors"
          >
            Continue
          </button>
        </div>
      )}

      {state.step === 3 && (
        <div className="space-y-4">
          <h2 className="text-sm font-semibold">Test Connection</h2>
          <p className="text-xs text-muted-foreground">
            We&apos;ll verify that your API key works with the selected provider.
          </p>
          {state.validationResult && (
            <div
              className={`p-3 rounded-md text-sm ${
                state.validationResult.valid
                  ? "bg-green-50 text-green-700 border border-green-200"
                  : "bg-red-50 text-red-700 border border-red-200"
              }`}
            >
              {state.validationResult.message}
            </div>
          )}
          <div className="flex gap-3">
            <button
              onClick={handleValidate}
              disabled={state.validating}
              className="flex-1 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 text-white text-sm font-medium py-2 px-4 rounded-md transition-colors"
            >
              {state.validating ? "Testing..." : "Test Connection"}
            </button>
            <button
              onClick={() => setState((prev) => ({ ...prev, step: 4 }))}
              className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium py-2 px-4 rounded-md transition-colors"
            >
              Skip
            </button>
          </div>
        </div>
      )}

      {state.step === 4 && (
        <div className="text-center space-y-4">
          <div className="text-4xl">🎉</div>
          <h2 className="text-lg font-semibold">All Set!</h2>
          <p className="text-sm text-muted-foreground">
            Your Recruitment Assistant is configured and ready to use.
          </p>
          <p className="text-xs text-muted-foreground">
            {state.validationResult?.valid
              ? "API key validated successfully."
              : "Configuration saved. You can update it later."}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium py-2 px-6 rounded-md transition-colors"
          >
            Start Using
          </button>
        </div>
      )}
    </div>
  );
}
