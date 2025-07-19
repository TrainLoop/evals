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
    private flushImmediately = false;

    get isFlushImmediate(): boolean {
        return this.flushImmediately;
    }

    constructor(exportAtInterval?: number, exportAtLength?: number, flushImmediately?: boolean) {
        this.exportAtInterval = exportAtInterval ?? this.exportAtInterval;
        this.exportAtLength = exportAtLength ?? this.exportAtLength;
        this.flushImmediately = flushImmediately ?? false;
        
        logger.debug(`FileExporter created with settings:`);
        logger.debug(`  exportAtInterval: ${this.exportAtInterval}ms`);
        logger.debug(`  exportAtLength: ${this.exportAtLength} calls`);
        logger.debug(`  flushImmediately: ${this.flushImmediately}`);
        
        // Start periodic flush timer only when NOT in flushImmediately mode
        if (!this.flushImmediately) {
            logger.debug(`Starting periodic flush timer (${this.exportAtInterval}ms)`);
            this.exportInterval = setInterval(() => {
                logger.debug("Periodic flush timer fired");
                this.export();
            }, this.exportAtInterval);
        } else {
            logger.debug("Flush immediately mode enabled, no timer started");
        }
    }

    /**
     * Record an LLM API call for later export
     */
    recordLLMCall(callData: LLMCallData): void {
        // Only record if it's an LLM request
        if (callData.isLLMRequest) {
            this.callBuffer.push(callData);
            logger.debug(`Recorded LLM call, buffer size now: ${this.callBuffer.length}`);
            logger.debug(`Call details: URL=${callData.url}, Tag=${callData.tag || '(none)'}`);
            
            if (this.flushImmediately) {
                logger.debug("Flush immediately mode - exporting now");
                this.export();
            } else if (this.callBuffer.length >= this.exportAtLength) {
                logger.debug(`Buffer size (${this.callBuffer.length}) reached threshold (${this.exportAtLength}) - exporting now`);
                this.export();
            } else {
                logger.debug(`Buffer size (${this.callBuffer.length}) below threshold (${this.exportAtLength}) - waiting`);
            }
        } else {
            logger.debug("Not an LLM request, skipping record");
        }
    }

    /**
     * Export collected LLM call data to storage
     */
    private export(): boolean {
        logger.debug(`export() called, buffer size: ${this.callBuffer.length}`);
        
        if (this.exportingFlag) {
            logger.warn(`Export already in progress, skipping export`);
            return false;
        }
        
        if (this.callBuffer.length === 0) {
            logger.debug("No calls to export, skipping");
            return false;
        }
        
        this.exportingFlag = true;
        logger.debug("Starting export...");
        logger.debug(`Exporting ${this.callBuffer.length} LLM calls`);
        const folder = process.env.TRAINLOOP_DATA_FOLDER;
        if (!folder) {
            logger.error("TRAINLOOP_DATA_FOLDER not set → calls not exported");
            this.exportingFlag = false;
            return false;
        }

        // Copy & clear buffer atomically to avoid writing duplicates if timer
        // fires while we are exporting (especially when flushImmediately=true).
        const toWrite = this.callBuffer;
        this.callBuffer = [];
        logger.debug(`Cleared buffer, processing ${toWrite.length} calls`);

        try {
            const samples: CollectedSample[] = [];
            for (const call of toWrite) {
                // Skip if not an LLM request or missing request body
                if (!call.isLLMRequest || !call.requestBodyStr) {
                    logger.debug(`Skipping non-LLM or empty request: isLLM=${call.isLLMRequest}, hasBody=${!!call.requestBodyStr}`);
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
                logger.info(`Saving ${samples.length} samples to ${folder}`);
                saveSamples(folder, samples);
            } else {
                logger.warn("No valid samples to save after processing");
            }
            this.exportingFlag = false;
            logger.debug("Export complete");
            return true;
        } catch (error: unknown) {
            logger.error(`Failed to export calls to ${folder}: ${error}`);
            logger.debug(`Error details: ${error instanceof Error ? error.stack : String(error)}`);
            // Put the calls back in the buffer so they're not lost
            this.callBuffer = [...toWrite, ...this.callBuffer];
            logger.debug(`Restored ${toWrite.length} calls to buffer for retry`);
            this.exportingFlag = false;
            return false;
        }
    }

    /**
     * Force export of any buffered calls
     */
    flush(): boolean {
        logger.debug(`Flushing FileExporter - buffer size: ${this.callBuffer.length}`);
        const result = this.export();
        logger.debug(`Flush result: ${result}`);
        return result;
    }

    /**
     * Clean up and perform final export
     */
    shutdown(): void {
        logger.debug(`Shutting down FileExporter - buffer size: ${this.callBuffer.length}`);
        if (this.callBuffer.length > 0) {
            logger.info(`Exporting ${this.callBuffer.length} buffered calls before shutdown`);
            this.export();
        }
        if (this.exportInterval) {
            logger.debug("Clearing export interval timer");
            clearInterval(this.exportInterval);
            this.exportInterval = null;
        }
        logger.debug("FileExporter shutdown complete");
    }

    /**
     * Clear all buffered calls without exporting
     */
    clear(): void {
        const count = this.callBuffer.length;
        this.callBuffer = [];
        logger.debug(`Cleared ${count} calls from buffer`);
    }
}