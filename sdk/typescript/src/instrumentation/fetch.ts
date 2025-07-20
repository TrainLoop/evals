import { getExpectedLlmProviderUrls } from "../env";
import { HEADER_NAME } from "../constants";
import { FileExporter } from "../exporter";
import { getAndRemoveHeader, getCallerSite, getCallerStack, getFetchHost, cloneResponseForLogging } from "./utils";
import { createLogger } from "../logger";

const logger = createLogger("trainloop-fetch");

/* ------------- patch fetch ------------- */

export function patchFetch(exporter: FileExporter): void {
    logger.debug(`[PATCH START] globalThis.fetch type: ${typeof globalThis.fetch}`);
    logger.debug(`[PATCH START] globalThis.fetch name: ${globalThis.fetch?.name}`);
    logger.debug(`[PATCH START] globalThis === global: ${globalThis === global}`);
    
    if (typeof globalThis.fetch === "function") {
        const origFetch = globalThis.fetch;
        logger.debug(`[PATCH] Captured original fetch: ${origFetch.name}`);

        globalThis.fetch = (async function patchedFetch(
            resource: RequestInfo | URL,
            init: RequestInit = {},
        ): Promise<Response> {
            logger.debug(`[FETCH INTERCEPTED] ${resource} with method ${init.method || 'GET'}`);
            const t0 = Date.now();
            // Remove and retrieve the X-Trainloop-Tag header
            let tagValue: string | undefined;
            if (init && init.headers) {
                tagValue = getAndRemoveHeader(init.headers, HEADER_NAME);
            }

            const location = getCallerSite(getCallerStack());

            const reqBody =
                init.body && typeof init.body !== "string" ? "[stream]" : init.body ?? "";

            // Real fetch
            const res = await origFetch(resource, init);

            // Fire-and-forget logging
            (async () => {
                const host = getFetchHost(resource);
                logger.debug(`[FETCH HOST] Extracted host: ${host}`);
                const allowedUrls = getExpectedLlmProviderUrls();
                logger.debug(`[FETCH ALLOWLIST] Checking against: ${allowedUrls.join(', ')}`);
                
                if (host && allowedUrls.includes(host)) {
                    logger.debug(`[FETCH MATCH] Host ${host} is in allowlist, logging LLM call`);
                    // Clone response without blocking
                    const resBody = await cloneResponseForLogging(res);
                    const t1 = Date.now();
                    const ms = t1 - t0;

                    logger.info("------- START FETCH CALL -------");
                    logger.info(`Method: ${init.method ?? "GET"}`);
                    logger.info(`Resource: ${resource}`);
                    logger.info(`Request Body: ${reqBody}`);
                    logger.info(`Status: ${res.status}`);
                    logger.info(`Response Body: ${resBody}`);
                    logger.info(`Duration: ${ms} ms`);
                    logger.info(`Location: ${JSON.stringify(location)}`);
                    logger.info(`Tag: ${tagValue}`);
                    logger.info("------- END FETCH CALL   -------");

                    exporter.recordLLMCall({
                        requestBodyStr: reqBody,
                        responseBodyStr: resBody,
                        durationMs: Math.round(ms),
                        url: resource.toString(),
                        endTimeMs: Math.round(t1),
                        startTimeMs: Math.round(t0),
                        isLLMRequest: true,
                        location,
                        status: res.status,
                        tag: tagValue,

                    })
                } else {
                    logger.debug(`Host ${host} not in allowlist, skipping`);
                }
            })().catch((err) => {
                /* swallow logging errors so they never affect the main flow */
                logger.error(`Error in fetch logging: ${err}`);
            });
            // Caller receives stream immediately
            return res;
        }) as typeof fetch;
        
        logger.debug(`[PATCH COMPLETE] globalThis.fetch assigned`);
        logger.debug(`[PATCH COMPLETE] globalThis.fetch.name: ${globalThis.fetch.name}`);
        logger.debug(`[PATCH COMPLETE] globalThis.fetch === origFetch: ${globalThis.fetch === origFetch}`);
        logger.debug(`[PATCH COMPLETE] globalThis.fetch toString starts with: ${globalThis.fetch.toString().slice(0, 50)}`);
        logger.debug(`Fetch patching complete. New fetch function: ${globalThis.fetch.name}`);
    } else {
        logger.warn("Global fetch not found, skipping patch");
    }
}
