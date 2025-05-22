import { getResult } from '@/database/results'

// Define interfaces for type safety
interface ResultRow {
  rowid: number;
  ts: string;
  suite: string;
  metric: string;
  passed: number;
  reason: string | null;
  filename: string;
  sample?: {
    entries?: {
      tag?: string;
      model?: string;
      duration_ms?: number;
      [key: string]: any;
    };
    [key: string]: any;
  };
  [key: string]: any;
}

function SectionHeader({ title }: { title: string }) {
  return <h2 className="text-lg font-medium text-white mt-6 mb-2 border-b border-gray-700 pb-1">{title}</h2>;
}

function MetadataItem({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex mb-1">
      <div className="w-32 font-medium text-gray-400">{label}:</div>
      <div className="text-white">{value}</div>
    </div>
  );
}

function JsonViewer({ data }: { data: any }) {
  if (!data) return null;
  return (
    <pre className="p-3 rounded-md text-sm overflow-auto max-h-96 bg-gray-800 text-gray-300">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}

function stringValue(value: any): string {
  return value === null || value === undefined ? '' : String(value);
}

export default async function ResultDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const rawRow = await getResult(id);

  if (!rawRow) {
    return <div className="p-4">Result not found</div>;
  }

  // Cast to our typed interface
  const row = rawRow as unknown as ResultRow;

  return (
    <div className="max-w-4xl">
      <div className="flex items-center gap-3 mb-4">
        <h1 className="text-2xl font-semibold text-white">Result Details</h1>
        <span
          className={`px-3 py-1 rounded-full text-sm font-medium ${row.passed ? 'bg-green-800 text-green-200' : 'bg-red-800 text-red-200'}`}
        >
          {row.passed ? 'PASS' : 'FAIL'}
        </span>
      </div>

      <div className="rounded-lg shadow-sm border border-gray-700 p-6 bg-gray-900">
        <SectionHeader title="Basic Information" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8">
          <MetadataItem label="Row ID" value={stringValue(row.rowid)} />
          <MetadataItem label="Timestamp" value={stringValue(row.ts)} />
          <MetadataItem label="Suite" value={stringValue(row.suite)} />
          <MetadataItem label="Metric" value={stringValue(row.metric)} />
          <MetadataItem
            label="Passed"
            value={
              <span className={row.passed ? 'text-green-400' : 'text-red-400'}>
                {row.passed ? '✓ Yes' : '✗ No'}
              </span>
            }
          />
          <MetadataItem
            label="Reason"
            value={row.reason || <span className="text-gray-500 italic">None</span>}
          />
        </div>

        <SectionHeader title="File Location" />
        <MetadataItem
          label="Path"
          value={
            <code className="bg-gray-800 px-2 py-1 rounded text-sm text-gray-300">
              {stringValue(row.filename)}
            </code>
          }
        />

        {row.sample && typeof row.sample === 'object' && (
          <>
            <SectionHeader title="Sample Data" />
            {row.sample.entries && typeof row.sample.entries === 'object' && (
              <div className="space-y-4">
                {row.sample.entries.tag && (
                  <MetadataItem label="Tag" value={stringValue(row.sample.entries.tag)} />
                )}
                {row.sample.entries.model && (
                  <MetadataItem label="Model" value={stringValue(row.sample.entries.model)} />
                )}
                {row.sample.entries.duration_ms && (
                  <MetadataItem label="Duration" value={`${row.sample.entries.duration_ms}ms`} />
                )}

                <details className="mt-4">
                  <summary className="cursor-pointer font-medium p-2 rounded bg-gray-800 text-gray-300 hover:bg-gray-700">View Sample Details</summary>
                  <div className="p-2 pt-4 border border-gray-700 rounded-b bg-gray-900 mt-1">
                    <JsonViewer data={row.sample} />
                  </div>
                </details>
              </div>
            )}
          </>
        )}

        <details className="mt-6">
          <summary className="cursor-pointer font-medium p-2 rounded bg-gray-800 text-gray-300 hover:bg-gray-700">View Raw JSON</summary>
          <div className="p-2 pt-4 border border-gray-700 rounded-b bg-gray-900 mt-1">
            <JsonViewer data={row} />
          </div>
        </details>
      </div>
    </div>
  );
}
