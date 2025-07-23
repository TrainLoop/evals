import { patchHttp } from "./instrumentation/http";
import http from "http";
import https from "https";
import { patchFetch } from "./instrumentation/fetch";
import { FileExporter } from "./exporter"
import { loadConfig } from "./config";
import { HEADER_NAME, DEFAULT_HOST_ALLOWLIST } from "./constants";

/**
 * Public surface:
 *  • HEADER_NAME      - constant header string
 *  • trainloopTag(tag)   - helper to add the trainloop tag to the header
 *  • shutdown()       - graceful shutdown
 */

export { HEADER_NAME, DEFAULT_HOST_ALLOWLIST };

/**
 * Convenience helper - merge into your fetch/OpenAI headers
 */
export function trainloopTag(tag: string): Record<string, string> {
  return { [HEADER_NAME]: tag };
}

// Global exporter instance
let globalExporter: FileExporter | null = null;

const init = async () => {
  // First load the config from the trainloop folder if available
  loadConfig();
  await import("./instrumentation");
  globalExporter = new FileExporter();
  patchHttp(http, globalExporter);
  patchHttp(https, globalExporter);
  patchFetch(globalExporter);
}

// Initialize the SDK
init();

/**
 * Graceful shutdown - exports remaining data and cleans up resources
 */
export async function shutdown(): Promise<void> {
  if (globalExporter) {
    globalExporter.shutdown();
    globalExporter = null;
  }
}

// host allow‑list
export const EXPECTED_LLM_PROVIDER_URLS = (process.env.TRAINLOOP_HOST_ALLOWLIST ?? DEFAULT_HOST_ALLOWLIST.join(","))
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);
