interface LLMCallLocation {
    file?: string;
    lineNumber: string;
}

type ParsedRequestMessage = {
    role: string;
    content: string;
};

type ParsedResponseBody = {
    content: string;
};

export interface CollectedSample {
    tag: string;
    model: string;
    durationMs: number;
    startTimeMs: number; // Unix timestamp
    endTimeMs: number; // Unix timestamp
    input: ParsedRequestMessage[];
    output: ParsedResponseBody;
    modelParams: Record<string, unknown>;
    url: string;
    location: LLMCallLocation;
}
export type EventsTable = CollectedSample;

export interface ResultsTable {
    metric: string;
    sample: CollectedSample;
    passed: number; // 1 or 0
    reason: string | null;
}

export type RegistryEntry = {
    lineNumber: string;
    tag: string;
    firstSeen: string;   // ISO-8601 UTC
    lastSeen: string;
    count: number;
};

export type Registry = {
    schema: number;
    files: {
        [file: string]: {
            [line: string]: RegistryEntry;
        };
    };
};

export interface Database {
    events: EventsTable;
    results: ResultsTable;
    registry: Registry;
}