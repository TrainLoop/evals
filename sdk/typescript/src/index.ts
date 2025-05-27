import { patchHttp } from "./instrumentation/http";
import http from "http";
import https from "https";
import { patchFetch } from "./instrumentation/fetch";
import { FileExporter } from "./exporter"
import { loadConfig } from "./config";

/**
 * Public surface:
 *  • HEADER_NAME      - constant header string
 *  • trainloopTag(tag)   - helper to add the trainloop tag to the header
 *  • installHooks()   - manual bootstrap (rarely needed)
 */

export const HEADER_NAME = "X-Trainloop-Tag";

/**
 * Convenience helper - merge into your fetch/OpenAI headers
 */
export function trainloopTag(tag: string): Record<string, string> {
  return { [HEADER_NAME]: tag };
}

export const DEFAULT_HOST_ALLOWLIST = ["api.openai.com", "api.anthropic.com"];

const init = async () => {
  // First load the config from the trainloop folder if available
  loadConfig();
  await import("./instrumentation");
  const exporter = new FileExporter();
  patchHttp(http, exporter);
  patchHttp(https, exporter);
  patchFetch(exporter);
}

init();

// host allow‑list
export const EXPECTED_LLM_PROVIDER_URLS = (process.env.TRAINLOOP_HOST_ALLOWLIST ?? DEFAULT_HOST_ALLOWLIST.join(","))
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);
