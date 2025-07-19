import { patchHttp } from "./instrumentation/http";
import http from "http";
import https from "https";
import { patchFetch } from "./instrumentation/fetch";
import { FileExporter } from "./exporter"
import { loadConfig } from "./config";
import { HEADER_NAME, DEFAULT_HOST_ALLOWLIST } from "./constants";
import { createLogger } from "./logger";

const logger = createLogger("trainloop-init");

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
  logger.debug(`collect() called with flushImmediately=${flushImmediately}`);
  
  if (isInitialized) {
    logger.debug("SDK already initialized, skipping");
    return;
  }

  // First load the config from the trainloop folder if available
  logger.debug("Loading config...");
  loadConfig();
  
  if (!process.env.TRAINLOOP_DATA_FOLDER) {
    logger.warn("TRAINLOOP_DATA_FOLDER not set - SDK disabled");
    console.warn("[TrainLoop] TRAINLOOP_DATA_FOLDER not set - SDK disabled");
    return;
  }
  
  logger.debug(`Initializing with data folder: ${process.env.TRAINLOOP_DATA_FOLDER}`);
  logger.debug(`Host allowlist: ${process.env.TRAINLOOP_HOST_ALLOWLIST}`);
  logger.debug(`Log level: ${process.env.TRAINLOOP_LOG_LEVEL}`);

  logger.debug("Importing instrumentation module...");
  await import("./instrumentation");
  
  logger.debug(`Creating FileExporter with flushImmediately=${flushImmediately}`);
  globalExporter = new FileExporter(undefined, undefined, flushImmediately);
  
  logger.debug("Patching http module...");
  patchHttp(http, globalExporter);
  
  logger.debug("Patching https module...");
  patchHttp(https, globalExporter);
  
  logger.debug("Patching global fetch...");
  patchFetch(globalExporter);
  
  isInitialized = true;
  logger.info("TrainLoop Evals SDK initialized successfully");
  console.log("[TrainLoop] TrainLoop Evals SDK initialized");
}

// Initialize the SDK automatically
logger.debug("Auto-initializing SDK...");
collect().catch(err => {
  logger.error(`Auto-initialization failed: ${err}`);
  console.error("[TrainLoop] Auto-initialization failed:", err);
});

/**
 * Manually flush any buffered LLM calls to disk.
 * Useful for testing or when you want to ensure data is written immediately.
 */
export async function flush(): Promise<void> {
  logger.debug("flush() called");
  if (globalExporter) {
    logger.debug("Flushing exporter...");
    globalExporter.flush();
  } else {
    logger.warn("SDK not initialized - call collect() first");
    console.warn("[TrainLoop] SDK not initialized - call collect() first");
  }
}

/**
 * Graceful shutdown - exports remaining data and cleans up resources
 */
export async function shutdown(): Promise<void> {
  logger.debug("shutdown() called");
  if (globalExporter) {
    logger.debug("Shutting down exporter...");
    globalExporter.shutdown();
    globalExporter = null;
    isInitialized = false;
    logger.info("SDK shutdown complete");
  } else {
    logger.debug("No exporter to shutdown");
  }
}

// host allow‑list
export const EXPECTED_LLM_PROVIDER_URLS = (process.env.TRAINLOOP_HOST_ALLOWLIST ?? DEFAULT_HOST_ALLOWLIST.join(","))
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);

logger.debug(`Configured LLM provider URLs: ${EXPECTED_LLM_PROVIDER_URLS.join(", ")}`);
