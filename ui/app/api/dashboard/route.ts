import { NextResponse } from 'next/server';
import { getDuckDB } from '@/database/duckdb';
import { convertBigIntsToNumbers } from '@/utils/json-helpers';

export interface ModelStats {
  calls: number;
  p50_ms: number;
  p95_ms: number;
  accuracy: number;
}

export interface MetricStats {
  pass_rate: number;
  runs: number;
}

export interface MetricTrendPoint {
  bucket: string;
  pass_rate: number;
}

export interface MetricModelUsage {
  model: string;
  metric: string;
  runs: number;
}

export interface TopLocation {
  file: string;
  calls: number;
}

export interface DashboardPayload {
  timestamp: number;
  global: {
    calls_24h: number;
    median_latency_ms: number;
    overall_pass_rate: number;
  };
  models: Record<string, ModelStats>;
  metrics: Record<string, MetricStats>;
  metric_trend: MetricTrendPoint[];
  metric_model_usage: MetricModelUsage[];
  top_locations: TopLocation[];
}

export async function GET() {
  try {
    const db = await getDuckDB();
    const conn = await db.connect();

    try {
      const dayAgo = Date.now() - 24 * 60 * 60 * 1000;
      
      // Get global stats from the database
      const globalReader = await conn.runAndReadAll(`
        SELECT COUNT(*) AS calls_24h,
               approx_quantile(durationMs, 0.5) AS median_latency_ms,
               (SELECT AVG(passed) FROM results) AS overall_pass_rate
        FROM events
        WHERE epoch_ms(startTimeMs) > ${dayAgo};
      `);

      const globalRows = globalReader.getRowObjects();
      const globalData = {
        calls_24h: 0,
        median_latency_ms: 0,
        overall_pass_rate: 0,
        ...(globalRows.length > 0 ? convertBigIntsToNumbers(globalRows[0]) as {
          calls_24h: number;
          median_latency_ms: number;
          overall_pass_rate: number;
        } : {})
      };

      // Get model stats
      const modelReader = await conn.runAndReadAll(`
        SELECT sample.model AS model,
               COUNT(*) AS calls,
               approx_quantile(sample.duration_ms, 0.5) AS p50_ms,
               approx_quantile(sample.duration_ms, 0.95) AS p95_ms,
               AVG(passed) AS accuracy
        FROM results
        GROUP BY sample.model;
      `);

      const modelRows = convertBigIntsToNumbers(modelReader.getRowObjects());
      const models: Record<string, ModelStats> = {};

      // Process model data and collect p50 values
      const allP50s: number[] = [];
      for (const row of modelRows) {
        if (typeof row.model === 'string') {
          const p50 = typeof row.p50_ms === 'number' ? row.p50_ms : 0;
          models[row.model] = {
            calls: typeof row.calls === 'number' ? row.calls : 0,
            p50_ms: p50,
            p95_ms: typeof row.p95_ms === 'number' ? row.p95_ms : 0,
            accuracy: typeof row.accuracy === 'number' ? row.accuracy : 0,
          };
          if (p50 > 0) {
            allP50s.push(p50);
          }
        }
      }

      // Calculate global median latency
      let globalMedianLatency = 0;
      if (globalData.median_latency_ms > 0) {
        // Use the global median if available
        globalMedianLatency = globalData.median_latency_ms;
      } else if (allP50s.length > 0) {
        // Otherwise calculate median of model p50s
        allP50s.sort((a, b) => a - b);
        const mid = Math.floor(allP50s.length / 2);
        globalMedianLatency = allP50s.length % 2 !== 0
          ? allP50s[mid]
          : Math.round((allP50s[mid - 1] + allP50s[mid]) / 2);
      }

      // Create the payload structure
      const payload: DashboardPayload = {
        timestamp: Date.now(),
        global: {
          calls_24h: globalData.calls_24h || 0,
          median_latency_ms: globalMedianLatency,
          overall_pass_rate: globalData.overall_pass_rate || 0,
        },
        models,
        metrics: {},
        metric_trend: [],
        metric_model_usage: [],
        top_locations: [],
      };

      // Metric stats - Performance by metric
      const metricReader = await conn.runAndReadAll(`
      SELECT metric,
             AVG(passed) AS pass_rate,
             COUNT(*) AS runs
      FROM results
      GROUP BY metric;
    `);

      const metricRows = convertBigIntsToNumbers(metricReader.getRowObjects());
      for (const row of metricRows) {
        // Only add metric data if the metric name is a string
        if (typeof row.metric === 'string') {
          payload.metrics[row.metric] = {
            pass_rate: typeof row.pass_rate === 'number' ? row.pass_rate : 0,
            runs: typeof row.runs === 'number' ? row.runs : 0,
          };
        }
      }

      // Metric trend - Last 7 days, hourly buckets
      const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
      const trendReader = await conn.runAndReadAll(`
      SELECT date_trunc('hour', to_timestamp(sample.start_time_ms/1000)) AS bucket,
             AVG(passed) AS pass_rate
      FROM results
      WHERE sample.start_time_ms > ${weekAgo}
      GROUP BY bucket
      ORDER BY bucket;
    `);

      const rawTrend = convertBigIntsToNumbers(trendReader.getRowObjects());
      // Ensure metric_trend only contains valid data points
      payload.metric_trend = rawTrend
        .filter(row =>
          typeof row.bucket === 'string' &&
          typeof row.pass_rate === 'number'
        )
        .map(row => ({
          bucket: String(row.bucket),
          pass_rate: Number(row.pass_rate)
        }));

      // Metric × Model usage
      const usageReader = await conn.runAndReadAll(`
      SELECT sample.model AS model, 
             metric,
             COUNT(*) AS runs
      FROM results
      GROUP BY sample.model, metric;
    `);

      const rawUsage = convertBigIntsToNumbers(usageReader.getRowObjects());
      // Ensure metric_model_usage only contains valid data points
      payload.metric_model_usage = rawUsage
        .filter(row =>
          typeof row.model === 'string' &&
          typeof row.metric === 'string' &&
          typeof row.runs === 'number'
        )
        .map(row => ({
          model: String(row.model),
          metric: String(row.metric),
          runs: Number(row.runs)
        }));

      // Top 5 code locations by call volume
      const locationReader = await conn.runAndReadAll(`
      SELECT location.file AS file,
             COUNT(*) AS calls
      FROM events
      GROUP BY file
      ORDER BY calls DESC
      LIMIT 5;
    `);

      const rawLocations = convertBigIntsToNumbers(locationReader.getRowObjects());
      // Ensure top_locations only contains valid data points
      payload.top_locations = rawLocations
        .filter(row =>
          typeof row.file === 'string' &&
          typeof row.calls === 'number'
        )
        .map(row => ({
          file: String(row.file),
          calls: Number(row.calls)
        }));

      return NextResponse.json(payload, { status: 200 });
    } catch (error) {
      console.error('Error generating dashboard data:', error);
      return NextResponse.json(
        { error: 'Failed to generate dashboard data', details: error instanceof Error ? error.message : String(error) },
        { status: 500 }
      );
    } finally {
      conn.closeSync();
    }
  } catch (dbError) {
    // Handle issues with getting the database connection
    console.error('Database connection error:', dbError);

    return NextResponse.json(
      { error: 'Database connection failed', details: dbError instanceof Error ? dbError.message : String(dbError) },
      { status: 500 }
    );
  }
}
