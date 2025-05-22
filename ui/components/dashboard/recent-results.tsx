'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Skeleton } from '@/components/ui/skeleton';
import { formatDistanceToNow } from 'date-fns';
import { CheckCircle2, XCircle } from 'lucide-react';

interface Result {
  rowid: string;
  metric: string;
  passed: number;
  reason: string | null;
  sample: {
    entries: Array<{
      input?: string;
      output?: string;
      [key: string]: unknown;
    }>;
  };
  ts: string;
  suite: string;
}

export function RecentResults() {
  const [results, setResults] = useState<Result[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const res = await fetch('/api/results?limit=5');
        if (res.ok) {
          const data = await res.json();
          setResults(data);
        }
      } catch (error) {
        console.error('Error fetching results:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, []);

  const getContentPreview = (result: Result) => {
    try {
      const firstSample = result.sample?.entries?.[0];
      if (!firstSample) return 'No sample data';

      const content = firstSample.input || firstSample.output || JSON.stringify(firstSample);
      return content.length > 50 ? `${content.substring(0, 50)}...` : content;
    } catch (error) {
      console.error('Error getting content preview:', error);
      return 'Preview unavailable';
    }
  };

  const formatResultTime = (timestamp: string) => {
    try {
      const timestampMs = Number(timestamp) * 1000;
      if (isNaN(timestampMs)) return 'Recent';
      return formatDistanceToNow(new Date(timestampMs), { addSuffix: true });
    } catch (error) {
      console.error('Error formatting time:', error);
      return 'Recent';
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="flex items-center space-x-4 p-2 border rounded">
            <Skeleton className="h-4 w-4 rounded-full" />
            <div className="space-y-2 flex-1">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-1/2" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="text-center p-4">
        <p className="text-sm text-muted-foreground">No evaluation results found</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {results.map((result) => (
        <Link
          key={result.rowid}
          href={`/results?ts=${result.ts}&suite=${encodeURIComponent(result.suite)}`}
          className="block p-3 rounded-md hover:bg-accent transition-colors border"
        >
          <div className="flex justify-between items-start">
            <div className="flex items-center space-x-2">
              {result.passed ? (
                <CheckCircle2 className="h-4 w-4 text-green-500" />
              ) : (
                <XCircle className="h-4 w-4 text-red-500" />
              )}
              <div>
                <h4 className="text-sm font-medium leading-none">
                  {result.metric}
                </h4>
                <p className="text-sm text-muted-foreground line-clamp-1">
                  {getContentPreview(result)}
                </p>
              </div>
            </div>
            <div className="text-xs text-muted-foreground">
              {formatResultTime(result.ts)}
            </div>
          </div>
          <div className="mt-1">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
              {result.suite || 'Default Suite'}
            </span>
          </div>
        </Link>
      ))}
      <div className="mt-4 text-center">
        <Link
          href="/results"
          className="inline-flex items-center text-sm font-medium text-primary hover:underline"
        >
          View all results <span className="ml-1">→</span>
        </Link>
      </div>
    </div>
  );
}
