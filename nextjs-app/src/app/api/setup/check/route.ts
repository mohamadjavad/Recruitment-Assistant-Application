import { NextRequest } from "next/server";

/**
 * GET /api/setup/check
 *
 * Checks if the environment is properly configured.
 * Reads .env variables and reports which required keys are missing.
 *
 * This is a STUB — the backend engineer will wire actual env checking.
 *
 * Response:
 *   { configured: boolean, missing_keys: string[], provider: string | null }
 */

const REQUIRED_KEYS = ["OPENAI_API_KEY", "SERPER_API_KEY"];

export async function GET(request: NextRequest) {
  // In a real implementation, this would read from the server's environment
  // or attempt to read the .env file from the parent directory.
  // For now, return a stub response.

  const missingKeys: string[] = [];
  for (const key of REQUIRED_KEYS) {
    if (!process.env[key]) {
      missingKeys.push(key);
    }
  }

  return new Response(
    JSON.stringify({
      configured: missingKeys.length === 0,
      missing_keys: missingKeys,
      provider: process.env["LLM_MODEL"] || "glm-5.2",
      message:
        missingKeys.length > 0
          ? `Missing API keys: ${missingKeys.join(", ")}. Use the setup wizard to configure.`
          : "Environment is configured and ready.",
    }),
    {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }
  );
}
