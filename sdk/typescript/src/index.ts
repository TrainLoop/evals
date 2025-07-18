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
let isInitialized = false;

/**
 * Initialize the SDK (idempotent). Does nothing unless
 * TRAINLOOP_DATA_FOLDER is set.
 * 
 * @param flushImmediately - If true, flush each LLM call immediately (useful for testing)
 */
export async function collect(flushImmediately: boolean = false): Promise<void> {
  if (isInitialized) {
    return;
  }

  // First load the config from the trainloop folder if available
  loadConfig();
  
  if (!process.env.TRAINLOOP_DATA_FOLDER) {
    console.warn("[TrainLoop] TRAINLOOP_DATA_FOLDER not set - SDK disabled");
    return;
  }

  await import("./instrumentation");
  globalExporter = new FileExporter(undefined, undefined, flushImmediately);
  patchHttp(http, globalExporter);
  patchHttp(https, globalExporter);
  patchFetch(globalExporter);
  
  isInitialized = true;
  console.log("[TrainLoop] TrainLoop Evals SDK initialized");
}

// Initialize the SDK automatically
collect();

/**
 * Manually flush any buffered LLM calls to disk.
 * Useful for testing or when you want to ensure data is written immediately.
 */
export async function flush(): Promise<void> {
  if (globalExporter) {
    globalExporter.flush();
  } else {
    console.warn("[TrainLoop] SDK not initialized - call collect() first");
  }
}

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
