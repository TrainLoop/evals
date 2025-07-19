import { patchHttp } from "./instrumentation/http";
import http from "http";
import https from "https";
import { patchFetch } from "./instrumentation/fetch";
import { FileExporter } from "./exporter";
import { loadConfig } from "./config";
import { HEADER_NAME, DEFAULT_HOST_ALLOWLIST } from "./constants";
import { createLogger } from "./logger";
import { getExpectedLlmProviderUrls } from "./env";

const logger = createLogger("trainloop-init");

/**
 * Public surface:
 *  • HEADER_NAME      - constant header string
 *  • trainloopTag(tag)   - helper to add the trainloop tag to the header
 *  • shutdown()       - graceful shutdown
 */

export { HEADER_NAME, DEFAULT_HOST_ALLOWLIST, getExpectedLlmProviderUrls };

/**
 * Convenience helper - merge into your fetch/OpenAI headers
 */
export function trainloopTag(tag: string): Record<string, string> {
  return { [HEADER_NAME]: tag };
}

// Global exporter instance
let globalExporter: FileExporter | null = null;
let isInitialized = false;

// Track HTTP client libraries that were imported before SDK initialization
const importedLibraries = new Set<string>();

// Common HTTP client libraries to check
const HTTP_CLIENT_LIBS = ["openai", "anthropic", "@anthropic-ai/sdk", "axios", "got", "node-fetch", "superagent"];

// Check if problematic libraries are loaded
function checkForEarlyImports(): void {
  logger.debug(`Checking for early imports of HTTP client libraries...`);
  
  // Check require.cache for any modules that might contain HTTP clients
  const cacheKeys = Object.keys(require.cache);
  
  for (const lib of HTTP_CLIENT_LIBS) {
    // Check if the library name appears in any cached module path
    const found = cacheKeys.some(key => {
      const normalizedKey = key.replace(/\\/g, '/');
      return normalizedKey.includes(`/node_modules/${lib}/`) || 
             normalizedKey.includes(`/${lib}/index.js`) ||
             normalizedKey.endsWith(`/${lib}.js`);
    });
    
    if (found) {
      logger.debug(`Found early import of ${lib}`);
      importedLibraries.add(lib);
    }
  }
  
  logger.debug(`Early imports found: ${Array.from(importedLibraries).join(', ') || 'none'}`);
}

/**
 * Initialize the SDK (idempotent). Does nothing unless
 * TRAINLOOP_DATA_FOLDER is set.
 * 
 * @param flushImmediately - If true, flush each LLM call immediately (useful for testing)
 */
export function collect(flushImmediately: boolean = false): void {
  logger.debug(`collect() called with flushImmediately=${flushImmediately}`);
  
  // Check for early imports before initialization
  checkForEarlyImports();
  
  // Always load the config in case the config path changed
  logger.debug("Loading config...");
  loadConfig();
  
  if (isInitialized) {
    // If SDK is already initialized, check if this is a different configuration
    const currentFlushMode = globalExporter ? globalExporter.isFlushImmediate : false;
    
    if (currentFlushMode !== flushImmediately) {
      logger.warn(`SDK already initialized with flushImmediately=${currentFlushMode}, reinitializing with flushImmediately=${flushImmediately}`);
      console.warn(
        `[TrainLoop] SDK is being re-initialized with different settings.\n` +
        `When using NODE_OPTIONS="--require=trainloop-llm-logging" the SDK auto-initializes, so you typically only need to call collect() if you want to change settings – for example to enable instant-flush during debugging.`
      );
      
      // Shutdown existing exporter
      if (globalExporter) {
        globalExporter.shutdown();
      }
      
      // Continue with reinitialization
      isInitialized = false;
    } else {
      logger.debug("SDK already initialized with same settings, skipping");
      console.info(
        `[TrainLoop] SDK already initialized - additional collect() calls are only necessary if you wish to modify settings (e.g., enable/disable instant flush).`
      );
      return;
    }
  }
  
  // Warn about early imports
  if (importedLibraries.size > 0 && !isInitialized) {
    const libs = Array.from(importedLibraries).join(", ");
    const errorMessage = `
╔═══════════════════════════════════════════════════════════════════════════════╗
║ TrainLoop SDK Warning: HTTP client libraries imported before initialization   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ The following libraries were imported before TrainLoop SDK was initialized:   ║
║ ${libs.padEnd(77)} ║
║                                                                               ║
║ This prevents the SDK from capturing LLM calls correctly.                    ║
║                                                                               ║
║ Fix: Move these lines to the very top of your entry point:                   ║
║   import { collect } from 'trainloop-llm-logging';                           ║
║   await collect();                                                            ║
║   // then import {${libs}} and other libraries                               ║
║                                                                               ║
║ The SDK needs to patch HTTP libraries before they create client instances.    ║
╚═══════════════════════════════════════════════════════════════════════════════╝`;
    
    logger.error(errorMessage);
    console.error(errorMessage);
    
    // Throw error to make it clear this needs to be fixed
    throw new Error(`TrainLoop SDK must be initialized before importing '${libs}'.\nThis prevents the SDK from capturing LLM calls correctly.\nFix: Move 'import { collect } from \"trainloop-llm-logging\"; collect();' to the very top of your entry point.`);
  }
  
  if (!process.env.TRAINLOOP_DATA_FOLDER) {
    logger.warn("TRAINLOOP_DATA_FOLDER not set - SDK disabled");
    console.warn("[TrainLoop] TRAINLOOP_DATA_FOLDER not set - SDK disabled");
    return;
  }
  
  logger.debug(`Initializing with data folder: ${process.env.TRAINLOOP_DATA_FOLDER}`);
  logger.debug(`Host allowlist: ${process.env.TRAINLOOP_HOST_ALLOWLIST}`);
  logger.debug(`Log level: ${process.env.TRAINLOOP_LOG_LEVEL}`);

  logger.debug("Importing instrumentation module...");
  require("./instrumentation");

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

// Initialize the SDK automatically (unless disabled)
if (!process.env.TRAINLOOP_DISABLE_AUTO_INIT) {
  logger.debug("Auto-initializing SDK...");
  try {
    collect();
  } catch (err) {
    logger.error(`Auto-initialization failed: ${err}`);
    console.error("[TrainLoop] Auto-initialization failed:", err);
  }
} else {
  logger.debug("Auto-initialization disabled via TRAINLOOP_DISABLE_AUTO_INIT");
}

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

