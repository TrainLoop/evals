export type CollectedSample = {
    durationMs: number;
    tag: string;
    input: ParsedRequestBody["messages"];
    output: ParsedResponseBody;
    model: string;
    modelParams: Record<string, unknown>;
    startTimeMs: number; // unix timestamp
    endTimeMs: number; // unix timestamp
    url: string;
    location: LLMCallLocation;
}

export type ParsedResponseBody = Record<"content", string>;

// OpenAI/Anthropic format
export type OpenAIRequestBody = {
    messages: Record<string, string>[];
    model: string;
    [key: string]: unknown;
}

// Google Gemini format
export type GeminiRequestBody = {
    contents: Array<{
        role?: string;
        parts: Array<{
            text?: string;
            inlineData?: string;
            fileData?: string;
        }>;
    }>;
    generationConfig?: {
        model?: string;
        temperature?: number;
        maxOutputTokens?: number;
        responseMimeType?: string;
        [key: string]: unknown;
    };
    safetySettings?: unknown[];
    tools?: unknown[];
    toolConfig?: unknown;
    systemInstruction?: unknown;
    [key: string]: unknown;
}

export type ExpectedRequestBody = OpenAIRequestBody | GeminiRequestBody;

export type ParsedRequestBody = {
    messages: Record<string, string>[];
    model: string;
    modelParams: Record<string, unknown>;
}

export type TrainloopConfig = {
    trainloop: {
        data_folder: string;
        host_allowlist: string[];
        log_level: string;
        flush_immediately?: boolean;
    }
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


export type LLMCallLocation = {
    file: string;
    lineNumber: string;
};

export type LLMCallData = {
    requestBodyStr?: string;
    responseBodyStr?: string;
    url?: string;
    tag?: string;
    location?: LLMCallLocation;
    startTimeMs?: number;
    endTimeMs?: number;
    durationMs?: number;
    isLLMRequest?: boolean;
    headers?: Record<string, string>;
    status?: number;
};