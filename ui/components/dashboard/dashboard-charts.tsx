import { useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { DashboardPayload, MetricModelUsage, TopLocation } from '@/app/api/dashboard/route';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, LineChart, Line, CartesianGrid } from 'recharts';

// Color palette for charts
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658'];

// Chart components
export function GlobalKPIStrip({ data }: { data: DashboardPayload }) {
  const { global } = data;

  return (
    <div className="grid gap-4 grid-cols-3">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Calls (24h)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{global.calls_24h.toLocaleString()}</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Median Latency</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{global.median_latency_ms.toLocaleString()} ms</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Pass Rate</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{(global.overall_pass_rate * 100).toFixed(1)}%</div>
        </CardContent>
      </Card>
    </div>
  );
}

export function ModelTrafficShare({ data }: { data: DashboardPayload }) {
  const pieData = useMemo(() => {
    return Object.entries(data.models).map(([name, stats]) => ({
      name,
      value: stats.calls,
    }));
  }, [data.models]);

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Traffic Share</CardTitle>
        <CardDescription>Calls by model</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => value.toLocaleString()} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

export function ModelLatency({ data }: { data: DashboardPayload }) {
  const barData = useMemo(() => {
    return Object.entries(data.models).map(([name, stats]) => ({
      name,
      p50: stats.p50_ms,
      p95: stats.p95_ms,
    }));
  }, [data.models]);

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Latency p50/p95</CardTitle>
        <CardDescription>Response time in milliseconds</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] -ml-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={barData}
              layout="vertical"
              margin={{ left: 20, right: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis
                dataKey="name"
                type="category"
                width={120}
                tick={{ fontSize: 12, width: 120 }}
                tickFormatter={(value) => {
                  // Truncate long labels and add ellipsis
                  const maxLength = 20;
                  return value.length > maxLength
                    ? `${value.substring(0, maxLength)}...`
                    : value;
                }}
              />
              <Tooltip
                formatter={(value) => `${value} ms`}
                labelFormatter={(value) => `Model: ${value}`}
              />
              <Legend />
              <Bar dataKey="p50" fill="#0088FE" name="p50 Latency" />
              <Bar dataKey="p95" fill="#FF8042" name="p95 Latency" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

export function ModelAccuracy({ data }: { data: DashboardPayload }) {
  const barData = useMemo(() => {
    return Object.entries(data.models).map(([name, stats]) => ({
      name,
      accuracy: stats.accuracy * 100, // Convert to percentage
    }));
  }, [data.models]);

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Accuracy by Model</CardTitle>
        <CardDescription>Pass rate percentage</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 100]} />
              <Tooltip formatter={(value) => `${typeof value === 'number' ? value.toFixed(1) : value}%`} />
              <Bar dataKey="accuracy" fill="#00C49F" name="Accuracy" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

export function MetricPassRates({ data }: { data: DashboardPayload }) {
  const barData = useMemo(() => {
    return Object.entries(data.metrics)
      .map(([name, stats]) => ({
        name,
        pass_rate: stats.pass_rate * 100, // Convert to percentage
        runs: stats.runs,
      }))
      .sort((a, b) => b.pass_rate - a.pass_rate); // Sort by pass_rate descending
  }, [data.metrics]);

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Metric Pass Rates</CardTitle>
        <CardDescription>Success rate by metric</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 100]} />
              <YAxis dataKey="name" type="category" width={100} />
              <Tooltip
                formatter={(value, name) => [`${typeof value === 'number' ? value.toFixed(1) : value}%`, 'Pass Rate']}
                labelFormatter={(name) => `${name} (${barData.find(d => d.name === name)?.runs || 0} runs)`}
              />
              <Bar dataKey="pass_rate" fill="#0088FE" name="Pass Rate" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

export function MetricTrend({ data }: { data: DashboardPayload }) {
  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Pass Rate Trend</CardTitle>
        <CardDescription>Last 7 days (hourly)</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data.metric_trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="bucket"
                tickFormatter={(value) => {
                  const date = new Date(value);
                  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:00`;
                }}
              />
              <YAxis domain={[0, 1]} tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
              <Tooltip
                formatter={(value) => {
                  const numValue = Number(value);
                  return isNaN(numValue) ? [String(value), 'Pass Rate'] : [`${(numValue * 100).toFixed(1)}%`, 'Pass Rate'];
                }}
                labelFormatter={(value) => {
                  try {
                    const date = new Date(value);
                    return date.toLocaleString();
                  } catch (e) {
                    return String(value);
                  }
                }}
              />
              <Line type="monotone" dataKey="pass_rate" stroke="#8884d8" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

export function MetricModelHeatmap({ data }: { data: DashboardPayload }) {
  // Process data for the heatmap
  const models = useMemo(() => {
    return [...new Set(data.metric_model_usage.map(item => item.model))];
  }, [data.metric_model_usage]);

  const metrics = useMemo(() => {
    return [...new Set(data.metric_model_usage.map(item => item.metric))];
  }, [data.metric_model_usage]);

  const getRunsForPair = (model: string, metric: string): number => {
    const item = data.metric_model_usage.find(
      item => item.model === model && item.metric === metric
    );
    return item ? item.runs : 0;
  };

  const getColorIntensity = (runs: number): string => {
    const maxRuns = Math.max(...data.metric_model_usage.map(item => item.runs));
    const intensity = Math.min(0.1 + (runs / maxRuns) * 0.9, 1);
    return `rgba(0, 136, 254, ${intensity})`;
  };

  return (
    <Card className="col-span-2">
      <CardHeader>
        <CardTitle>Metric x Model Usage</CardTitle>
        <CardDescription>Run counts by metric and model</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                <th className="p-2 border"></th>
                {models.map(model => (
                  <th key={model} className="p-2 border text-xs font-medium">
                    {model}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {metrics.map(metric => (
                <tr key={metric}>
                  <td className="p-2 border text-xs font-medium">{metric}</td>
                  {models.map(model => {
                    const runs = getRunsForPair(model, metric);
                    return (
                      <td
                        key={`${model}-${metric}`}
                        className="p-2 border text-center text-xs"
                        style={{ backgroundColor: getColorIntensity(runs) }}
                      >
                        {runs > 0 ? runs : ''}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

export function TopLocationsTable({ data }: { data: DashboardPayload }) {
  return (
    <Card className="col-span-2">
      <CardHeader>
        <CardTitle>Top Code Locations</CardTitle>
        <CardDescription>Most frequent call sites</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">File Path</th>
                <th className="text-right p-2">Calls</th>
              </tr>
            </thead>
            <tbody>
              {data.top_locations.map((location, index) => (
                <tr key={index} className="border-b">
                  <td className="text-left p-2 text-sm font-mono">{location.file}</td>
                  <td className="text-right p-2">{location.calls.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
