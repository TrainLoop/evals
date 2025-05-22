'use client';

import { useEffect, useState } from 'react';
import { DashboardPayload } from '@/app/api/dashboard/route';
import {
  GlobalKPIStrip,
  ModelTrafficShare,
  ModelLatency,
  ModelAccuracy,
  MetricPassRates,
  MetricTrend,
  MetricModelHeatmap,
  TopLocationsTable
} from './dashboard-charts';

export default function DashboardContent() {
  const [dashboardData, setDashboardData] = useState<DashboardPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        const response = await fetch('/api/dashboard');
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        const data = await response.json();
        setDashboardData(data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setLoading(false);
      }
    }

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="py-6">
        <div className="text-center">
          <p className="text-sm text-muted-foreground">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (error || !dashboardData) {
    // If we can't load real data, use mock data for demonstration
    console.log('Using mock data for dashboard visualization');

    // Create mock dashboard data
    const mockData: DashboardPayload = {
      timestamp: Date.now(),
      global: {
        calls_24h: 328,
        median_latency_ms: 450,
        overall_pass_rate: 0.92,
      },
      models: {
        'gpt-3.5-turbo': {
          calls: 120,
          p50_ms: 350,
          p95_ms: 780,
          accuracy: 0.88,
        },
        'claude-3-5-sonnet': {
          calls: 208,
          p50_ms: 550,
          p95_ms: 980,
          accuracy: 0.95,
        },
      },
      metrics: {
        'always_pass': {
          pass_rate: 1.0,
          runs: 50,
        },
        'factual_accuracy': {
          pass_rate: 0.85,
          runs: 120,
        },
        'code_correctness': {
          pass_rate: 0.91,
          runs: 82,
        },
      },
      metric_trend: Array.from({ length: 24 }, (_, i) => ({
        bucket: new Date(Date.now() - (23 - i) * 60 * 60 * 1000).toISOString(),
        pass_rate: 0.75 + Math.random() * 0.2,
      })),
      metric_model_usage: [
        { model: 'gpt-3.5-turbo', metric: 'always_pass', runs: 25 },
        { model: 'gpt-3.5-turbo', metric: 'factual_accuracy', runs: 45 },
        { model: 'gpt-3.5-turbo', metric: 'code_correctness', runs: 50 },
        { model: 'claude-3-5-sonnet', metric: 'always_pass', runs: 25 },
        { model: 'claude-3-5-sonnet', metric: 'factual_accuracy', runs: 75 },
        { model: 'claude-3-5-sonnet', metric: 'code_correctness', runs: 32 },
      ],
      top_locations: [
        { file: '/pages/api/openai-fetch.ts', calls: 85 },
        { file: '/fastapi_server/routes/anthropic_sdk.py', calls: 62 },
        { file: '/app/chat/action.ts', calls: 47 },
        { file: '/lib/providers/openai.ts', calls: 31 },
        { file: '/src/client/api.ts', calls: 28 },
      ],
    };

    // Show notification about using demonstration data
    return (
      <>
        <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
          <p className="text-yellow-800">
            ⚠️ <strong>Database Connection Issue:</strong> {error || 'Could not connect to the database'}
          </p>
          <p className="text-sm text-yellow-700 mt-1">
            Showing demonstration data instead. The dashboard visualizations below use mock data for preview purposes.
          </p>
        </div>


        {/* Model Performance Section */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-3">🤖 Model Performance</h2>
          <div className="flex flex-col gap-4">
            <ModelTrafficShare data={mockData} />
            <ModelLatency data={mockData} />
            <ModelAccuracy data={mockData} />
          </div>
        </div>

        {/* Metric Insights Section */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-3">📐 Metric Insights</h2>
          <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-2 mb-4">
            <MetricPassRates data={mockData} />
            <MetricTrend data={mockData} />
          </div>
          <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-2">
            <MetricModelHeatmap data={mockData} />
            <TopLocationsTable data={mockData} />
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      {/* Global KPI Strip */}
      <div className="mb-6 mt-6">
        <GlobalKPIStrip data={dashboardData} />
      </div>

      {/* Model Performance Section */}
      <div className="mb-6 mt-6">
        <h2 className="text-xl font-semibold mb-3">🤖 Model Performance</h2>
        <div className="flex flex-col gap-4">
          <ModelTrafficShare data={dashboardData} />
          <ModelLatency data={dashboardData} />
          <ModelAccuracy data={dashboardData} />
        </div>
      </div>

      {/* Metric Insights Section */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-3">📐 Metric Insights</h2>
        <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-2 mb-4">
          <MetricPassRates data={dashboardData} />
          <MetricTrend data={dashboardData} />
        </div>
        <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-2">
          <MetricModelHeatmap data={dashboardData} />
          <TopLocationsTable data={dashboardData} />
        </div>
      </div>
    </>
  );
}
