import { DuckDBInstance } from '@duckdb/node-api';
import { existsSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

let cached: DuckDBInstance | null = null;
// Flag to track if views are being initialized to prevent concurrent initializations
let isInitializingViews = false;
// Flag to track if views have been successfully initialized
let viewsInitialized = false;

function findJsonlFiles(dir: string, pattern?: string): string[] {
  if (!existsSync(dir)) return [];

  try {
    if (pattern === 'nested') {
      // For results directory: look in subdirectories
      const files: string[] = [];
      const subdirs = readdirSync(dir).filter(item => {
        const fullPath = join(dir, item);
        return statSync(fullPath).isDirectory();
      });

      for (const subdir of subdirs) {
        const subdirPath = join(dir, subdir);
        const jsonlFiles = readdirSync(subdirPath)
          .filter(file => file.endsWith('.jsonl'))
          .map(file => join(subdirPath, file));
        files.push(...jsonlFiles);
      }
      return files;
    } else {
      // For events directory: look directly in the directory
      return readdirSync(dir)
        .filter(file => file.endsWith('.jsonl'))
        .map(file => join(dir, file));
    }
  } catch (err) {
    console.warn(`Warning: Could not read directory ${dir}:`, err);
    return [];
  }
}

export async function getDuckDB(): Promise<DuckDBInstance> {
  if (cached) return cached;

  // During build time, this might be called for static analysis but we won't actually connect
  const ROOT = process.env.TRAINLOOP_DATA_FOLDER;

  if (!ROOT) {
    // During build time, this is expected - create a temporary in-memory database
    if (process.env.NODE_ENV === 'production' && !process.env.RUNTIME) {
      const db = await DuckDBInstance.fromCache(':memory:');
      return (cached = db);
    }
    console.error('❌ ERROR: TRAINLOOP_DATA_FOLDER environment variable is not set');
    process.exit(1);
  }

  // Check that the data folder exists
  if (!existsSync(ROOT)) {
    // During build time, this is expected - create a temporary in-memory database
    if (process.env.NODE_ENV === 'production' && !process.env.RUNTIME) {
      const db = await DuckDBInstance.fromCache(':memory:');
      return (cached = db);
    }
    console.error(`❌ ERROR: Data folder does not exist at path: ${ROOT}`);
    console.error('Please check your TRAINLOOP_DATA_FOLDER environment variable');
    process.exit(1);
  }

  console.log(`✅ Using data folder at path: ${ROOT}`);

  // Validate directory structure
  const eventsDir = join(ROOT, 'events');
  const resultsDir = join(ROOT, 'results');

  if (!existsSync(eventsDir)) {
    console.error(`❌ ERROR: Events directory does not exist at path: ${eventsDir}`);
    console.error('Please ensure your data folder has the correct structure');
    process.exit(1);
  }

  if (!existsSync(resultsDir)) {
    console.error(`❌ ERROR: Results directory does not exist at path: ${resultsDir}`);
    console.error('Please ensure your data folder has the correct structure');
    process.exit(1);
  }

  const db = await DuckDBInstance.fromCache(`${ROOT}/tl.duckdb`);

  // Only try to initialize views if they haven't been successfully initialized already
  if (!viewsInitialized) {
    await initViews(db, ROOT);
  }

  return (cached = db);
}

async function initViews(db: DuckDBInstance, ROOT: string) {
  // If already initialized, just return
  if (viewsInitialized) {
    return;
  }

  // If currently initializing, wait for it to complete
  if (isInitializingViews) {
    // Wait for initialization to complete (poll every 100ms, max 10 seconds)
    let attempts = 0;
    while (isInitializingViews && attempts < 100) {
      await new Promise(resolve => setTimeout(resolve, 100));
      attempts++;
    }
    return;
  }

  // Set flag to prevent concurrent initializations
  isInitializingViews = true;

  // Double-check after setting the flag
  if (viewsInitialized) {
    isInitializingViews = false;
    return;
  }

  const conn = await db.connect();

  try {
    // First install and load extensions
    try {
      await conn.run(`INSTALL json; LOAD json;`);
    } catch (err) {
      // Extensions already loaded, continue
    }

    // Check for existing views to avoid unnecessary recreation
    const viewCheckReader = await conn.runAndReadAll(
      `SELECT name FROM sqlite_master WHERE type='view' AND name IN ('events', 'results', 'registry')`
    );
    const existingViews = viewCheckReader.getRowObjects();
    const hasEventsView = existingViews.some(row => row.name === 'events');
    const hasResultsView = existingViews.some(row => row.name === 'results');
    const hasRegistryView = existingViews.some(row => row.name === 'registry');

    // Check for JSONL files in events directory
    const eventsFiles = findJsonlFiles(join(ROOT, 'events'));

    if (!hasEventsView) {
      if (eventsFiles.length === 0) {
        console.log('⚠️  No JSONL files found in events directory - creating empty events view');
        await conn.run(`
          CREATE VIEW events AS
          SELECT
            NULL::INTEGER AS rowid,
            NULL::VARCHAR AS tag,
            NULL::VARCHAR AS model,
            NULL::TIMESTAMP AS durationMs,
            NULL::TIMESTAMP AS startTimeMs,
            NULL::TIMESTAMP AS endTimeMs,
            NULL::JSON AS input,
            NULL::JSON AS output,
            NULL::JSON AS modelParams,
            NULL::VARCHAR AS url,
            NULL::JSON AS location
          WHERE 1=0
        `);
      } else {
        console.log(`✅ Found ${eventsFiles.length} JSONL files in events directory - creating events view`);
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
    }

    // Check for JSONL files in results directory (nested structure)
    const resultsFiles = findJsonlFiles(join(ROOT, 'results'), 'nested');

    if (!hasResultsView) {
      if (resultsFiles.length === 0) {
        console.log('⚠️  No JSONL files found in results directory - creating empty results view');
        await conn.run(`
          CREATE VIEW results AS
          SELECT
            NULL::INTEGER AS rowid,
            NULL::VARCHAR AS ts,
            NULL::VARCHAR AS suite,
            NULL::VARCHAR AS metric,
            NULL::JSON AS sample,
            NULL::BOOLEAN AS passed,
            NULL::DOUBLE AS score,
            NULL::VARCHAR AS reason
          WHERE 1=0
        `);
      } else {
        console.log(`✅ Found ${resultsFiles.length} JSONL files in results directory - creating results view`);
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
    }

    // Handle registry
    const registryPath = join(ROOT, '_registry.json');

    if (!hasRegistryView) {
      if (existsSync(registryPath)) {
        console.log('✅ Found _registry.json - creating registry view');
        await conn.run(`
          CREATE VIEW registry AS
          SELECT * FROM read_json_auto('${registryPath}');
        `);
      } else {
        console.log('⚠️  No _registry.json found - creating empty registry view');
        await conn.run(`
          CREATE VIEW registry AS
          SELECT
            NULL::INTEGER AS schema,
            NULL::JSON AS files
          WHERE 1=0
        `);
      }
    }

    // Mark views as initialized if we get here without errors
    viewsInitialized = true;
    console.log('✅ Database views initialized successfully');
  } catch (err) {
    console.error('❌ Failed to initialize database views:', err);
    process.exit(1);
  } finally {
    // Reset flag when done
    isInitializingViews = false;
    conn.closeSync();
  }
}
