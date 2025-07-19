import { DEFAULT_HOST_ALLOWLIST } from "./constants";

/**
 * Derive the list of allowed LLM provider hostnames from the environment.
 * Falls back to {@link DEFAULT_HOST_ALLOWLIST} when the env var is not set.
 */
export function getExpectedLlmProviderUrls(): string[] {
  return (process.env.TRAINLOOP_HOST_ALLOWLIST ?? DEFAULT_HOST_ALLOWLIST.join(","))
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}