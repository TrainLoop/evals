import { DuckDBInstance } from '@duckdb/node-api';
import { existsSync } from 'node:fs';

let cached: DuckDBInstance | null = null;
// Flag to track if views are being initialized to prevent concurrent initializations
let isInitializingViews = false;
// Flag to track if views have been successfully initialized
let viewsInitialized = false;

export async function getDuckDB(): Promise<DuckDBInstance> {
  if (cached) return cached;

  const ROOT = process.env.TRAINLOOP_DATA_FOLDER!;

  if (!ROOT) {
    throw new Error("TRAINLOOP_DATA_FOLDER environment variable is not set");
  }

  // Check that this folder exists
  if (!existsSync(`${ROOT}`)) {
    throw new Error("Data folder does not exist");
  }

  const db = await DuckDBInstance.fromCache(`${ROOT}/tl.duckdb`);

  // Only try to initialize views if they haven't been successfully initialized already
  if (!viewsInitialized) {
    await initViews(db, ROOT);
  }

  return (cached = db);
}

async function initViews(db: DuckDBInstance, ROOT: string) {
  // Only one thread should initialize views at a time
  if (isInitializingViews) {
    // Another process is already initializing views, just return
    return;
  }

  // Set flag to prevent concurrent initializations
  isInitializingViews = true;

  // If views are already initialized, just return
  if (viewsInitialized) {
    isInitializingViews = false;
    return;
  }

  try {
    // Attempt to initialize views with retries
    await initializeWithRetry(db, ROOT);
    // Mark views as initialized if we get here without errors
    viewsInitialized = true;
  } catch (err) {
    console.error('Failed to initialize views after retries:', err);
  } finally {
    // Reset flag when done
    isInitializingViews = false;
  }
}

async function initializeWithRetry(db: DuckDBInstance, ROOT: string, maxRetries = 3) {
  let retries = 0;

  while (retries < maxRetries) {
    const conn = await db.connect();
    try {
      // First try to install and load extensions
      try {
        await conn.run(`INSTALL json; LOAD json;`);
      } catch (err) {
        // Extensions already loaded, continue
      }

      // First check if views already exist to avoid unnecessary recreation
      const viewCheckReader = await conn.runAndReadAll(
        `SELECT name FROM sqlite_master WHERE type='view' AND name IN ('events', 'results')`
      );
      const existingViews = viewCheckReader.getRowObjects() as any[];
      const hasEventsView = existingViews.some(row => row.name === 'events');
      const hasResultsView = existingViews.some(row => row.name === 'results');

      // Only create events view if it doesn't exist or we need to recreate it
      if (!hasEventsView) {
        await conn.run(`
          CREATE VIEW events AS
          SELECT
            CAST(row_number() OVER (ORDER BY startTimeMs) AS INTEGER) AS rowid,
            * REPLACE
            (
              TRIM(both '"' FROM tag)                  AS tag,          -- clean text
              epoch_ms(CAST(durationMs  AS BIGINT))    AS durationMs,   -- JS number
              epoch_ms(CAST(startTimeMs AS BIGINT))    AS startTimeMs,  -- JS number
              epoch_ms(CAST(endTimeMs   AS BIGINT))    AS endTimeMs,    -- JS number

              -- rebuild the nested "output" struct with cleaned content
              struct_pack(content := TRIM(both '"' FROM output.content)) AS output
            )
          FROM read_json_auto('${ROOT}/events/*.jsonl');
        `);
      }

      // Only create results view if it doesn't exist
      if (!hasResultsView) {
        await conn.run(`
          CREATE VIEW results AS
          SELECT
            CAST(row_number() OVER (ORDER BY regexp_extract(filename, '/results/([^/]+)/', 1) DESC) AS INTEGER) AS rowid,
            regexp_extract(filename, '/results/([^/]+)/', 1) AS ts,
            regexp_extract(filename, '/results/[^/]+/([^/]+)\.jsonl', 1) AS suite,
            *
          FROM read_json_auto('${ROOT}/results/*/*.jsonl', filename=true);
        `);
      }

      // If we get here, views were created or already existed
      return;
    } catch (err) {
      console.error(`View initialization attempt ${retries + 1} failed:`, err);
      retries++;

      // Wait a bit before retrying to allow other operations to complete
      if (retries < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, 100 * retries));
      }
    } finally {
      conn.closeSync();
    }
  }

  throw new Error('Failed to initialize views after maximum retries');
}
