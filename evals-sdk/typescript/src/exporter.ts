import { saveSamples, updateRegistry } from "./store";
import { createLogger } from "./logger";
import { CollectedSample, LLMCallData } from "./types/shared";
import { getCallerSite, getCallerStack, parseRequestBody, parseResponseBody } from "./instrumentation/utils";
import { inspect } from "util";

const logger = createLogger("trainloop-exporter");

export class FileExporter {
    private callBuffer: LLMCallData[] = [];
    private exportInterval: NodeJS.Timeout | null = null;
    private exportAtLength = 5;
    private exportAtInterval = 10000;
    private exportingFlag = false;

    constructor(exportAtInterval?: number, exportAtLength?: number) {
        this.exportAtInterval = exportAtInterval ?? this.exportAtInterval;
        this.exportAtLength = exportAtLength ?? this.exportAtLength;
        this.exportInterval = setInterval(() => this.export(), this.exportAtInterval);
    }

    /**
     * Record an LLM API call for later export
     */
    recordLLMCall(callData: LLMCallData): void {
        // Only record if it's an LLM request
        if (callData.isLLMRequest) {
            this.callBuffer.push(callData);
            logger.debug(`Recorded LLM call, new buffer: ${inspect(this.callBuffer)}`);
            if (this.callBuffer.length >= this.exportAtLength) {
                this.export();
            }
        }
    }

    /**
     * Export collected LLM call data to storage
     */
    private export(): boolean {
        if (this.exportingFlag) {
            logger.warn(`Export already in progress, skipping export`);
            return false;
        }
        this.exportingFlag = true;
        logger.debug(`Exporting ${this.callBuffer.length} LLM calls`);
        const folder = process.env.TRAINLOOP_DATA_FOLDER;
        if (!folder) {
            logger.error("TRAINLOOP_DATA_FOLDER not set → calls not exported");
            this.exportingFlag = false;
            return false;
        }

        try {
            const samples: CollectedSample[] = [];
            for (const call of this.callBuffer) {
                // Skip if not an LLM request or missing request body
                if (!call.isLLMRequest || !call.requestBodyStr) {
                    continue;
                }

                logger.info(`Processing call with URL ${call.url}`);

                // Parse the request body
                const parsedRequest = parseRequestBody(call.requestBodyStr);
                if (!parsedRequest) {
                    logger.error(`Failed to parse request body, skipping: ${call.requestBodyStr}`);
                    continue;
                }

                const parsedResponse = parseResponseBody(call.responseBodyStr ?? "");
                if (!parsedResponse) {
                    logger.error(`Failed to parse response body, skipping: ${call.responseBodyStr}`);
                    continue;
                }
                // the registry should be updated regardless of whether or not there is a tag
                const tag = call.tag ?? "";
                const location = call.location ?? getCallerSite(getCallerStack());

                // Update registry regardless of whether there's a tag
                updateRegistry(folder, location, tag ?? "untagged");

                // Prepare the sample
                const data: CollectedSample = {
                    durationMs: call.durationMs ?? Infinity,
                    tag: tag,
                    input: parsedRequest.messages,
                    output: parsedResponse,
                    model: parsedRequest.model ?? "Unknown",
                    modelParams: parsedRequest.modelParams ?? {},
                    startTimeMs: call.startTimeMs ?? 0,
                    endTimeMs: call.endTimeMs ?? Infinity,
                    url: call.url ?? '',
                    location,
                }
                samples.push(data);
            }

            // Save all samples at once
            if (samples.length > 0) {
                saveSamples(folder, samples);
                // Clear the buffer after successful export
                this.callBuffer = [];
            }
            this.exportingFlag = false;
            return true;
        } catch (error: unknown) {
            logger.error(`Failed to export calls to ${folder}: ${error}`);
            this.exportingFlag = false;
            return false;
        }
    }

    /**
     * Force export of any buffered calls
     */
    flush(): boolean {
        logger.debug(`Flushing FileExporter`);
        return this.export();
    }

    /**
     * Clean up and perform final export
     */
    shutdown(): void {
        logger.debug(`Shutting down FileExporter`);
        this.export();
        if (this.exportInterval) {
            clearInterval(this.exportInterval);
        }
    }

    /**
     * Clear all buffered calls without exporting
     */
    clear(): void {
        this.callBuffer = [];
    }
}