// store.ts  ────────────────────────────────────────────────────────────────
import { createLogger } from "./logger";
import { CollectedSample, LLMCallLocation, Registry, RegistryEntry } from "./types/shared";

const logger = createLogger("trainloop-store");

/* ------------------------------------------------------------------ */
/*  Node-detection & lazy requires                                    */
/* ------------------------------------------------------------------ */

const isNode =
    typeof window === "undefined" &&
    typeof process !== "undefined" &&
    !!process.versions?.node;

// Defer the require so bundlers don't try to resolve it in the browser
// eslint-disable-next-line @typescript-eslint/no-implied-eval
const fs: typeof import("fs") | null = isNode ? eval("require")("fs") : null;
// eslint-disable-next-line @typescript-eslint/no-implied-eval
const path: typeof import("path") | null = isNode ? eval("require")("path") : null;

/* ------------------------------------------------------------------ */
/*  Types & in-memory registry cache                                  */
/* ------------------------------------------------------------------ */

const REG_CACHE: Record<string, Registry> = {};

/* ------------------------------------------------------------------ */
/*  Public API                                                        */
/* ------------------------------------------------------------------ */

/**
 * Bump counter and persist _registry.json
 */

export function updateRegistry(
    dataDir: string,
    location: LLMCallLocation,
    tag: string
): void {
    if (!isNode || !fs || !path) {
        logger.debug("Not in Node.js environment, skipping registry update");
        return;
    }
    
    logger.debug(`Updating registry: dataDir=${dataDir}, location=${JSON.stringify(location)}, tag=${tag}`);

    const filePath = path.join(dataDir, "_registry.json");
    let reg: Registry;

    /* ---------- load or init ---------- */
    try {
        if (REG_CACHE[filePath]) {
            logger.debug(`Using cached registry for ${filePath}`);
            reg = REG_CACHE[filePath];
        } else {
            logger.debug(`Loading registry from ${filePath}`);
            reg = loadRegistry(filePath);
        }

        // Ensure reg has the expected structure
        if (!reg || typeof reg !== 'object') {
            reg = { schema: 1, files: {} };
        }

        // Ensure files property exists
        if (!reg.files) {
            reg.files = {};
        }
    } catch (error) {
        logger.debug(`Failed to load registry, creating new one: ${error}`);
        reg = { schema: 1, files: {} };
    }
    REG_CACHE[filePath] = reg;

    /* ---------- mutate in-memory ---------- */

    // Safely handle the location and file properties
    if (!location) {
        logger.error("Location is undefined, using default");
        location = { file: "unknown-file", lineNumber: "0" };
    }

    const fileName = location.file || "unknown-file";

    // Safely initialize the file block
    if (!reg.files[fileName]) {
        logger.debug(`Creating new file block for ${fileName}`);
        reg.files[fileName] = {};
    }

    const fileBlock = reg.files[fileName];

    const now = new Date().toISOString();

    // Safely handle the lineNumber property
    const lineNumber = location.lineNumber || "0";

    const entry = fileBlock[lineNumber];
    if (entry) {
        // Update existing entry
        logger.debug(`Updating existing entry for ${fileName}:${lineNumber}`);
        entry.tag = tag;
        entry.lineNumber = lineNumber;
        entry.lastSeen = now;
        entry.count++;
    } else {
        // Create new entry
        logger.debug(`Creating new entry for ${fileName}:${lineNumber}`);
        fileBlock[lineNumber] = {
            lineNumber: lineNumber,
            tag,
            firstSeen: now,
            lastSeen: now,
            count: 1,
        };
    }

    /* ---------- persist ---------- */
    try {
        // Ensure the data directory exists
        logger.debug(`Ensuring data directory exists: ${dataDir}`);
        fs.mkdirSync(dataDir, { recursive: true });

        // Write the updated registry to disk
        logger.debug(`Writing registry to: ${filePath}`);
        fs.writeFileSync(filePath, JSON.stringify(reg, null, 2));

        logger.debug(`Registry updated → ${fileName}:${lineNumber} (${tag})`);
    } catch (error) {
        logger.error(`Failed to update registry: ${error}`);
        logger.debug(`Error details: ${error instanceof Error ? error.stack : String(error)}`);
    }
}


/**
 * Append samples (JSONL) under events/<timestamp>.jsonl
 */
export function saveSamples(
    dataDir: string,
    samples: CollectedSample[],
): void {
    if (!isNode || !fs || !path) {
        logger.debug("Not in Node.js environment, skipping save");
        return; // browser → no-op
    }

    if (samples.length === 0) {
        logger.debug("No samples to save");
        return;
    }

    logger.debug(`Saving ${samples.length} samples to ${dataDir}`);
    const evDir = path.join(dataDir, "events");
    logger.debug(`Creating events directory: ${evDir}`);
    fs.mkdirSync(evDir, { recursive: true });

    const windowTime = 10 * 60 * 1000;

    // Find the most recent timestamped file in events/
    let targetTimestamp = Date.now();
    logger.debug(`Looking for recent event files in ${evDir}`);
    try {
        const files = fs.readdirSync(evDir)
            .filter(f => /^(\d+)\.jsonl$/.test(f))
            .map(f => parseInt(f.split(".")[0], 10))
            .filter(ts => !isNaN(ts));
        
        logger.debug(`Found ${files.length} existing event files`);
        
        if (files.length > 0) {
            const latest = Math.max(...files);
            const age = targetTimestamp - latest;
            logger.debug(`Most recent file timestamp: ${latest} (${age}ms ago)`);
            
            if (age < windowTime) { // within n minutes
                logger.debug(`Reusing recent file timestamp ${latest}`);
                targetTimestamp = latest;
            } else {
                logger.debug(`File too old (${age}ms > ${windowTime}ms), using new timestamp`);
            }
        } else {
            logger.debug("No existing event files found, using new timestamp");
        }
    } catch (e) {
        logger.warn(`Error checking for recent event shards: ${e}`);
    }

    const lines = samples.map(s => JSON.stringify(s));
    const filePath = path.join(evDir, `${targetTimestamp}.jsonl`);
    
    try {
        logger.debug(`Writing ${lines.length} lines to ${filePath}`);
        fs.appendFileSync(filePath, lines.join("\n") + "\n");
        logger.info(`Successfully saved ${samples.length} samples to ${filePath}`);
    } catch (error) {
        logger.error(`Failed to save samples: ${error}`);
        logger.debug(`Error details: ${error instanceof Error ? error.stack : String(error)}`);
    }
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                           */
/* ------------------------------------------------------------------ */

function loadRegistry(filePath: string): Registry {
    if (!isNode || !fs) {
        logger.debug("Not in Node.js environment, returning empty registry");
        return {} as Registry; // browser → empty object
    }
    
    try {
        logger.debug(`Attempting to load registry from ${filePath}`);
        const content = fs.readFileSync(filePath, "utf8");
        const registry = JSON.parse(content);
        logger.debug(`Successfully loaded registry with ${Object.keys(registry.files || {}).length} files`);
        return registry;
    } catch (error) {
        logger.debug(`Failed to load registry: ${error}`);
        return {} as Registry;
    }
}
