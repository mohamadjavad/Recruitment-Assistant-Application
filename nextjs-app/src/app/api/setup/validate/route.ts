import { NextRequest } from "next/server";

/**
 * POST /api/setup/validate
 *
 * Validates an API key by making a test request to the configured LLM provider.
 *
 * This is a STUB — the backend engineer will wire actual API validation
 * by calling the LLM provider's models endpoint with the provided key.
 *
 * Request:
 *   { provider: string, api_key: string, base_url?: string }
 *
 * Response:
 *   { valid: boolean, message: string, models?: string[] }
 */

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { provider, api_key, base_url } = body;

    if (!api_key) {
      return new Response(
        JSON.stringify({
          valid: false,
          message: "API key is required",
        }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    // ── Stub: Always return valid ───────────────────────────
    // Replace with real API validation:
    //
    // 1. Make a GET request to {base_url}/models with Authorization header
    // 2. If 200 OK → key is valid
    // 3. If 401/403 → key is invalid
    // 4. Handle network errors gracefully
    //
    // Provider detection:
    //   - "glm-5.2" | "openai" → check OPENAI_API_KEY format
    //   - "ollama" → check if Ollama is running locally
    //   - "custom" → validate the base_url is reachable

    return new Response(
      JSON.stringify({
        valid: true,
        message: `API key for ${provider || "unknown"} appears valid.`,
        provider: provider || "unknown",
      }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({
        valid: false,
        message: "Failed to validate API key",
        details: error instanceof Error ? error.message : String(error),
      }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
