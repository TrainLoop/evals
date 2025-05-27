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
    if (!isNode || !fs || !path) return;

    const filePath = path.join(dataDir, "_registry.json");
    let reg: Registry;

    /* ---------- load or init ---------- */
    try {
        reg = REG_CACHE[filePath] ?? loadRegistry(filePath);

        // Ensure reg has the expected structure
        if (!reg || typeof reg !== 'object') {
            reg = { schema: 1, files: {} };
        }

        // Ensure files property exists
        if (!reg.files) {
            reg.files = {};
        }
    } catch (error) {
        reg = { schema: 1, files: {} };
    }
    REG_CACHE[filePath] = reg;

    /* ---------- mutate in-memory ---------- */

    // Safely handle the location and file properties
    if (!location) {
        logger.error("Location is undefined");
        location = { file: "unknown-file", lineNumber: "0" };
    }

    const fileName = location.file || "unknown-file";

    // Safely initialize the file block
    if (!reg.files[fileName]) {
        reg.files[fileName] = {};
    }

    const fileBlock = reg.files[fileName];

    const now = new Date().toISOString();

    // Safely handle the lineNumber property
    const lineNumber = location.lineNumber || "0";

    const entry = fileBlock[lineNumber];
    if (entry) {
        // Update existing entry
        entry.tag = tag;
        entry.lineNumber = lineNumber;
        entry.lastSeen = now;
        entry.count++;
    } else {
        // Create new entry
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
        fs.mkdirSync(dataDir, { recursive: true });

        // Write the updated registry to disk
        fs.writeFileSync(filePath, JSON.stringify(reg, null, 2));

        logger.debug(`Registry updated → ${fileName}:${lineNumber} (${tag})`);
    } catch (error) {
        logger.error(`Failed to update registry: ${error}`);
    }
}


/**
 * Append samples (JSONL) under events/<timestamp>.jsonl
 */
export function saveSamples(
    dataDir: string,
    samples: CollectedSample[],
): void {
    if (!isNode || !fs || !path) return; // browser → no-op

    if (samples.length === 0) return;

    logger.debug(`Saving ${samples.length} samples.`);
    const evDir = path.join(dataDir, "events");
    fs.mkdirSync(evDir, { recursive: true });

    const windowTime = 10 * 60 * 1000;

    // Find the most recent timestamped file in events/
    let targetTimestamp = Date.now();
    try {
        const files = fs.readdirSync(evDir)
            .filter(f => /^(\d+)\.jsonl$/.test(f))
            .map(f => parseInt(f.split(".")[0], 10))
            .filter(ts => !isNaN(ts));
        if (files.length > 0) {
            const latest = Math.max(...files);
            if (targetTimestamp - latest < windowTime) { // within n minutes
                targetTimestamp = latest;
            }
        }
    } catch (e) {
        logger.warn(`Error checking for recent event shards: ${e}`);
    }

    const lines = samples.map(s => JSON.stringify(s));
    fs.appendFileSync(path.join(evDir, `${targetTimestamp}.jsonl`), lines.join("\n") + "\n");
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                           */
/* ------------------------------------------------------------------ */

function loadRegistry(filePath: string): Registry {
    if (!isNode || !fs) return {} as Registry; // browser → empty object
    try {
        return JSON.parse(fs.readFileSync(filePath, "utf8"));
    } catch {
        return {} as Registry;
    }
}
