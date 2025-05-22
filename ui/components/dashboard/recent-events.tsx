'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Skeleton } from '@/components/ui/skeleton';
import { formatDistanceToNow } from 'date-fns';

interface Event {
  rowid: number;
  tag: string;
  model: string;
  input: {
    items: Array<{
      entries: {
        role: string;
        content: string;
      };
    }>;
  };
  startTimeMs: number | { micros: number };
}

export function RecentEvents() {
  const [events, setEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await fetch('/api/events?limit=5');
        if (res.ok) {
          const data = await res.json();
          setEvents(data);
        }
      } catch (error) {
        console.error('Error fetching events:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEvents();
  }, []);

  const getTimeAgo = (timestamp: number | { micros: number }) => {
    const ms = typeof timestamp === 'number' ? timestamp : timestamp.micros / 1000;
    return formatDistanceToNow(new Date(ms), { addSuffix: true });
  };

  const getContentPreview = (event: Event) => {
    const userMessages = event.input.items
      .filter(item => item.entries?.role === 'user')
      .map(item => item.entries?.content);

    const content = userMessages[0] || event.input.items[0]?.entries?.content || 'No content';
    return content.length > 50 ? `${content.substring(0, 50)}...` : content;
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

  if (events.length === 0) {
    return (
      <div className="text-center p-4">
        <p className="text-sm text-muted-foreground">No events found</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {events.map((event) => (
        <Link
          key={event.rowid}
          href={`/events/${event.rowid}`}
          className="block p-3 rounded-md hover:bg-accent transition-colors border"
        >
          <div className="flex justify-between items-start">
            <div className="space-y-1">
              <h4 className="text-sm font-medium leading-none">
                {event.tag || 'Untagged Event'}
              </h4>
              <p className="text-sm text-muted-foreground line-clamp-1">
                {getContentPreview(event)}
              </p>
            </div>
            <div className="text-xs text-muted-foreground">
              {getTimeAgo(event.startTimeMs)}
            </div>
          </div>
          <div className="mt-1">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {event.model || 'Unknown Model'}
            </span>
          </div>
        </Link>
      ))}
      <div className="mt-4 text-center">
        <Link
          href="/events"
          className="inline-flex items-center text-sm font-medium text-primary hover:underline"
        >
          View all events <span className="ml-1">→</span>
        </Link>
      </div>
    </div>
  );
}
