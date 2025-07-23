import { ClientRequest } from "http";
import { ExpectedRequestBody, LLMCallLocation, ParsedRequestBody, ParsedResponseBody, OpenAIRequestBody, GeminiRequestBody } from "../types/shared";
import { Readable } from "stream";
import { createLogger } from "../logger";

const logger = createLogger("trainloop-instrumentation-utils");

/**
 * Captures the stack trace of the caller, excluding the top frames.
 * 
 * @returns A string containing the formatted stack trace starting from the caller
 */
export function getCallerStack(): string {
    const stack = new Error().stack?.split("\n").slice(3) ?? [];
    return stack.join("\n");
}

/**
 * Extracts the caller's file location from a stack trace.
 * Searches through stack trace lines to find the first non-node and non-node_modules file location.
 * 
 * @param stack The stack trace string to parse
 * @returns A string containing the file path or "unknown" if not found
 */
export function getCallerSite(stack: string): LLMCallLocation {
    const lines = stack.split("\n");
    for (const f of lines) {
        // Match (file:line:col) and extract file and line
        const m = f.match(/\((.*?):(\d+):\d+\)$/);
        if (m && !m[1].includes("node:") && !m[1].includes("node_modules"))
            return { file: m[1], lineNumber: m[2] };
    }
    return { file: "unknown", lineNumber: "0" };
}

/**
 * Gets the value of a header (case-insensitive) from a Headers object, plain object, or array of [key, value] pairs,
 * removes it from the headers, and returns the value.
 *
 * @param headers The headers object (Headers, Record<string, string>, or [string, string][]).
 * @param headerName The name of the header to get and remove.
 * @returns The value of the header if found, otherwise undefined.
 */
export function getAndRemoveHeader<T extends Headers | Record<string, string> | [string, string][]>(
    headers: T,
    headerName: string
): string | undefined {
    const lower = headerName.toLowerCase();

    if (headers instanceof Headers) {
        let requestedHeader: string | undefined;
        headers.forEach((value, key) => {
            if (key.toLowerCase() === lower) {
                headers.delete(key);
                requestedHeader = value;
            }
        });
        return requestedHeader;
    } else if (Array.isArray(headers)) {
        const idx = headers.findIndex(([key]) => key.toLowerCase() === lower);
        if (idx !== -1) {
            const value = headers[idx][1];
            headers.splice(idx, 1);
            return value;
        }
    } else if (
        typeof headers === 'object' &&
        headers !== null &&
        !Array.isArray(headers) &&
        !(headers instanceof Headers)
    ) {
        const recordHeaders = headers as Record<string, string | string[]>;
        for (const key in recordHeaders) {
            if (key.toLowerCase() === lower) {
                let value = recordHeaders[key];
                if (Array.isArray(value)) {
                    // protective guard against headers being arrays
                    value = value[0];
                }
                delete recordHeaders[key];
                return value;
            }
        }
    }
    return undefined;
}

/**
 * Escapes raw CR/LF characters that appear *inside* a quoted string.
 * (Outside strings, line breaks are perfectly legal JSON formatting.)
 */
export function escapeBareNewlinesInStrings(src: string): string {
    let out = "";
    let inString = false;
    let escapeNext = false;
    let quote: '"' | "'" | "" = "";

    for (let i = 0; i < src.length; i++) {
        const ch = src[i];

        if (!inString) {
            // entering a string?
            if (ch === '"' || ch === "'") {
                inString = true;
                quote = ch as '"' | "'";
            }
            out += ch;
            continue;
        }

        // ----- we are inside a string literal -----
        if (escapeNext) {
            // previous char was a backslash - just copy this one through
            out += ch;
            escapeNext = false;
            continue;
        }

        if (ch === "\\") {
            out += ch;
            escapeNext = true;
            continue;
        }

        // closing quote ends the string
        if (ch === quote) {
            inString = false;
            quote = "";
            out += ch;
            continue;
        }

        // raw newline or carriage-return → replace with \n / \r
        if (ch === "\n") {
            out += "\\n";
            continue;
        }
        if (ch === "\r") {
            out += "\\r";
            continue;
        }

        out += ch;
    }

    return out;
}

/**
 * Safely parses a JSON string into a JavaScript object.
 *
 * Handles the common edge-case where multi-line content was pasted
 * without escaping newlines inside the string.
 *
 * @param s The JSON string to parse.
 * @returns The parsed object, or `undefined` if parsing fails.
 */
export function safeJsonParse<T>(s: string): T | undefined {
    if (!s || s.trim() === "") return undefined;
    try {
        // First try normal parsing
        return JSON.parse(s) as T;
    } catch (err) {
        // If it fails, try with our escaped newlines approach
        try {
            const escaped = escapeBareNewlinesInStrings(s);
            if (escaped !== s) {
                return JSON.parse(escaped) as T;
            }
        } catch (_) {
            // Ignore errors in the fallback path
        }
    }
    return undefined;
}

/**
 * Type guard to check if a body is an OpenAI/Anthropic request
 */
function isOpenAIRequest(body: any): body is OpenAIRequestBody {
    return body && Array.isArray(body.messages) && typeof body.model === 'string';
}

/**
 * Type guard to check if a body is a Google Gemini request
 */
function isGeminiRequest(body: any): body is GeminiRequestBody {
    return body && Array.isArray(body.contents);
}

/**
 * Parse a request body string into a structured format with messages array.
 * 
 * @param s JSON string to parse
 * @returns Object with 'content' (array of message objects), 'model', and 'modelParams'
 */
export function parseRequestBody(s: string): ParsedRequestBody | undefined {
    const body = safeJsonParse<ExpectedRequestBody>(s);
    if (!body) {
        return undefined;
    }

    // Handle OpenAI/Anthropic format (messages + model)
    if (isOpenAIRequest(body)) {
        const { messages, model, ...modelParams } = body;
        return {
            messages,
            model,
            modelParams
        };
    }

    // Handle Google Gemini format (contents + generationConfig)
    if (isGeminiRequest(body)) {
        // Convert Gemini contents to messages format
        const messages = body.contents.map((content) => {
            if (content.parts && Array.isArray(content.parts)) {
                // Flatten parts into a single content string
                const contentText = content.parts
                    .map((part) => part.text || part.inlineData || part.fileData || '')
                    .filter(Boolean)
                    .join(' ');
                
                return {
                    role: content.role || 'user',
                    content: contentText
                };
            }
            return { role: content.role || 'user', content: '' };
        });

        // Extract model from generationConfig or URL context 
        // (Gemini model is often specified in the URL, not in the body)
        const model = body.generationConfig?.model || 'gemini/unknown';
        
        // Use generationConfig as modelParams, excluding model field
        const { model: _model, ...modelParams } = body.generationConfig || {};
        
        const additionalParams: Record<string, unknown> = {
            ...modelParams
        };
        
        // Include other top-level fields that might be relevant
        if (body.safetySettings) additionalParams.safetySettings = body.safetySettings;
        if (body.tools) additionalParams.tools = body.tools;
        if (body.toolConfig) additionalParams.toolConfig = body.toolConfig;
        if (body.systemInstruction) additionalParams.systemInstruction = body.systemInstruction;

        return {
            messages,
            model,
            modelParams: additionalParams
        };
    }

    logger.warn(`Skipping invalid request body for: ${s}`);
    return undefined;
}

/**
 * Parse a response body string into a simplified format with just content.
 * 
 * @param s JSON string to parse
 * @returns Object with just a 'content' key
 */
export function parseResponseBody(s: string): ParsedResponseBody | undefined {
    const body = safeJsonParse<any>(s);
    if (!body) {
        return undefined;
    }
    
    // If it already has content field, return that
    if (body.content) {
        return { content: body.content };
    }
    
    // Try to extract content from OpenAI format
    let content = body?.choices?.[0]?.message?.content || 
                 body?.choices?.[0]?.text;
    
    // Try to extract content from Anthropic format
    if (!content) {
        content = body?.content?.[0]?.text;
    }
    
    // Try to extract content from Google Gemini format
    if (!content && body?.candidates?.[0]) {
        const candidate = body.candidates[0];
        if (candidate.content?.parts?.[0]?.text) {
            content = candidate.content.parts[0].text;
        }
        // Handle streaming responses
        else if (candidate.text) {
            content = candidate.text;
        }
    }
    
    // Try to extract from direct text field (some Gemini responses)
    if (!content && body?.text) {
        content = body.text;
    }
    
    if (typeof content === 'string') {
        return { content };
    }
    
    return undefined;
}

export const reqBodies = new WeakMap<ClientRequest, Buffer>();

export function fullUrl(opts: any): string {
    if (typeof opts === "string") return opts;
    const proto =
        opts.protocol ??
        (opts.port === 443 || opts.defaultPort === 443 ? "https:" : "http:");
    return `${proto}//${opts.host ?? opts.hostname}${opts.path ?? ""}`;
}

export async function drain(r: Readable | AsyncIterable<unknown>): Promise<string> {
    const chunks: Buffer[] = [];
    for await (const c of r)
        chunks.push(Buffer.isBuffer(c) ? c : Buffer.from(c as string));
    return Buffer.concat(chunks).toString("utf8");
}

// Helper to get hostname from resource
export const getFetchHost = (resource: RequestInfo | URL): string | undefined => {
    try {
        if (typeof resource === "string") {
            return new URL(resource).hostname;
        } else if (resource instanceof URL) {
            return resource.hostname;
        } else if (typeof Request !== "undefined" && resource instanceof Request) {
            return new URL(resource.url).hostname;
        }
    } catch { }
    return undefined;
}

// Format streamed responses into a meaningful summary for logging
export function formatStreamedContent(raw: string): string {
    try {
        // ----- Regular JSON response (non-streaming) -----
        const js = JSON.parse(raw);
        const first = js?.choices?.[0];
        const content = first?.message?.content ?? (typeof first?.text === 'string' ? first.text : undefined);
        if (typeof content === 'string') {
            return JSON.stringify({ content });
        }
    } catch {
        // not a plain JSON response, fall through to streaming handlers
    }

    try {
        // Special handling for OpenAI streaming format
        if (raw.includes('data:') && raw.includes('"choices"')) {
            const contentPieces: string[] = [];
            const dataLines = raw.split('\n');

            for (const line of dataLines) {
                if (!line.startsWith('data:') || line.includes('[DONE]')) continue;

                const jsonStr = line.replace('data:', '').trim();
                if (!jsonStr) continue;

                const data = JSON.parse(jsonStr);
                if (data?.choices?.[0]?.delta?.content) {
                    contentPieces.push(data.choices[0].delta.content);
                }
            }

            const fullContent = contentPieces.join('');
            if (fullContent) {
                return JSON.stringify({ content: fullContent });
            }
        }

        // Special handling for Anthropic streaming format
        if (raw.includes('event:') && raw.includes('content_block_delta')) {
            const contentPieces: string[] = [];
            const lines = raw.split('\n');

            for (const line of lines) {
                if (!line.startsWith('data:')) continue;

                const jsonStr = line.replace('data:', '').trim();
                if (!jsonStr) continue;

                const data = JSON.parse(jsonStr);
                if (data.type === 'content_block_delta' && data.delta?.text) {
                    contentPieces.push(data.delta.text);
                }
            }

            const fullContent = contentPieces.join('');
            if (fullContent) {
                return JSON.stringify({ content: fullContent });
            }
        }
    } catch {
        // Fall back to the raw response if parsing fails
    }

    return raw.length > 500 ? raw.substring(0, 500) + '... [truncated]' : raw;
}

// Clone the response without blocking streaming
export async function cloneResponseForLogging(res: Response): Promise<string> {
    // If it's not a streaming response or doesn't have a body, just use text()
    if (!res.body || !res.headers.get('content-type')?.includes('text/event-stream')) {
        const text = await res.clone().text();
        // Format non-streaming responses too
        return formatStreamedContent(text);
    }

    // For streaming responses, we need to be careful to clone without consuming the stream
    const clone = res.clone();
    return new Promise((resolve) => {
        // Read from clone separately
        if (clone.body && typeof clone.body.getReader === 'function') {
            const reader = clone.body.getReader();
            const decoder = new TextDecoder();
            let result = '';

            function read() {
                reader.read().then(({ value, done }) => {
                    if (done) {
                        resolve(formatStreamedContent(result));
                        return;
                    }
                    result += decoder.decode(value, { stream: true });
                    read();
                }).catch(() => {
                    // If we fail to read the stream, just return what we have
                    resolve(formatStreamedContent(result));
                });
            }

            read();
        } else {
            // Fallback
            resolve('(unable to read streaming response)');
        }
    });
}

