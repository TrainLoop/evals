'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';

interface EventData {
  rowid: number;
  tag: string;
  model: string;
  input: {
    items: Array<{
      entries: {
        role: string;
        content: string;
      }
    }>
  };
  output: {
    entries: {
      content: string;
    }
  };
  durationMs: number | { micros: number };
  startTimeMs: number | { micros: number };
  endTimeMs: { micros: number };
  url: string;
  location: {
    entries: {
      file: string;
      lineNumber: string;
    }
  };
  modelParams: {
    entries: {
      max_tokens: number;
      system: any;
      temperature: number;
      stream: boolean;
    }
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

// Client component for event details page
export default function EventDetail() {
  const params = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [eventData, setEventData] = useState<EventData | null>(null);

  useEffect(() => {
    async function fetchEvent() {
      if (!params.id) {
        setError('Missing event ID');
        setLoading(false);
        return;
      }

      try {
        const res = await fetch(`/api/events/${params.id}`);

        if (!res.ok) {
          if (res.status === 404) {
            setError('Event not found');
          } else {
            setError(`Error fetching event: ${res.status} ${res.statusText}`);
          }
          setLoading(false);
          return;
        }

        const data = await res.json();
        setEventData(data);
        setLoading(false);
      } catch (err) {
        setError(`Error: ${err instanceof Error ? err.message : String(err)}`);
        setLoading(false);
      }
    }

    fetchEvent();
  }, [params.id]);

  // Show loading state
  if (loading) {
    return (
      <div className="max-w-4xl p-4">
        <h1 className="text-2xl font-semibold text-white mb-4">Event Details</h1>
        <div className="flex items-center justify-center py-8 text-white">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
          <span className="ml-2">Loading event data...</span>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="max-w-4xl p-4">
        <h1 className="text-2xl font-semibold text-white mb-4">Event Details</h1>
        <div className="bg-red-900 border border-red-700 text-red-300 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    );
  }

  if (!eventData) {
    return (
      <div className="max-w-4xl p-4">
        <h1 className="text-2xl font-semibold text-white mb-4">Event Details</h1>
        <div className="bg-yellow-900 border border-yellow-700 text-yellow-300 px-4 py-3 rounded">
          No event data found
        </div>
      </div>
    );
  }

  // Handle complex timestamp format (micros object)
  const startTimeMs = typeof eventData.startTimeMs === 'object' && 'micros' in eventData.startTimeMs
    ? Math.floor(Number(eventData.startTimeMs.micros) / 1000) 
    : (typeof eventData.startTimeMs === 'number' ? eventData.startTimeMs : 0);
  
  const timestamp = startTimeMs ? new Date(startTimeMs).toLocaleString() : 'Invalid Date';
  
  // Handle complex duration format (micros object)
  const durationMs = typeof eventData.durationMs === 'object' && 'micros' in eventData.durationMs
    ? Math.floor(Number(eventData.durationMs.micros) / 1000) 
    : (typeof eventData.durationMs === 'number' ? eventData.durationMs : 0);

  return (
    <div className="max-w-4xl">
      <div className="flex items-center gap-3 mb-4">
        <h1 className="text-2xl font-semibold text-white">Event Details</h1>
        <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-800 text-blue-200">
          {eventData.tag || 'Event'}
        </span>
      </div>

      <div className="rounded-lg shadow-sm border border-gray-700 p-6 bg-gray-900">
        <SectionHeader title="Basic Information" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8">
          <MetadataItem label="Row ID" value={stringValue(eventData.rowid)} />
          <MetadataItem label="Tag" value={stringValue(eventData.tag)} />
          <MetadataItem label="Model" value={stringValue(eventData.model)} />
          <MetadataItem label="Timestamp" value={timestamp} />
          <MetadataItem label="Duration" value={`${durationMs}ms`} />
          {eventData.url && (
            <MetadataItem label="URL" value={
              <code className="bg-gray-800 px-2 py-1 rounded text-sm text-gray-300">
                {stringValue(eventData.url)}
              </code>
            } />
          )}
        </div>

        {eventData.location && eventData.location.entries && (
          <>
            <SectionHeader title="Source Location" />
            <MetadataItem 
              label="File" 
              value={
                <code className="bg-gray-800 px-2 py-1 rounded text-sm text-gray-300">
                  {eventData.location.entries.file || 'Unknown'}
                </code>
              } 
            />
            {eventData.location.entries.lineNumber && (
              <MetadataItem label="Line" value={eventData.location.entries.lineNumber} />
            )}
          </>
        )}

        {eventData.input && (
          <>
            <SectionHeader title="Input" />
            <details className="mt-4">
              <summary className="cursor-pointer font-medium p-2 rounded bg-gray-800 text-gray-300 hover:bg-gray-700">View Input Data</summary>
              <div className="p-2 pt-4 border border-gray-700 rounded-b bg-gray-900 mt-1">
                <JsonViewer data={eventData.input} />
              </div>
            </details>
          </>
        )}

        {eventData.output && (
          <>
            <SectionHeader title="Output" />
            <details className="mt-4">
              <summary className="cursor-pointer font-medium p-2 rounded bg-gray-800 text-gray-300 hover:bg-gray-700">View Output Data</summary>
              <div className="p-2 pt-4 border border-gray-700 rounded-b bg-gray-900 mt-1">
                <JsonViewer data={eventData.output} />
              </div>
            </details>
          </>
        )}

        {eventData.modelParams && (
          <>
            <SectionHeader title="Model Parameters" />
            <details className="mt-4">
              <summary className="cursor-pointer font-medium p-2 rounded bg-gray-800 text-gray-300 hover:bg-gray-700">View Model Parameters</summary>
              <div className="p-2 pt-4 border border-gray-700 rounded-b bg-gray-900 mt-1">
                <JsonViewer data={eventData.modelParams} />
              </div>
            </details>
          </>
        )}
        
        <details className="mt-6">
          <summary className="cursor-pointer font-medium p-2 rounded bg-gray-800 text-gray-300 hover:bg-gray-700">View Raw JSON</summary>
          <div className="p-2 pt-4 border border-gray-700 rounded-b bg-gray-900 mt-1">
            <JsonViewer data={eventData} />
          </div>
        </details>
      </div>
    </div>
  );
}
