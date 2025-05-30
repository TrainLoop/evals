import { EXPECTED_LLM_PROVIDER_URLS, HEADER_NAME } from "../index";
import { FileExporter } from "../exporter";
import { getAndRemoveHeader, getCallerSite, getCallerStack, getFetchHost, cloneResponseForLogging } from "./utils";
import { createLogger } from "../logger";

const logger = createLogger("trainloop-fetch");

/* ------------- patch fetch ------------- */

export function patchFetch(exporter: FileExporter): void {
    if (typeof globalThis.fetch === "function") {
        const origFetch = globalThis.fetch;

        globalThis.fetch = (async function patchedFetch(
            resource: RequestInfo | URL,
            init: RequestInit = {},
        ): Promise<Response> {
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
                if (host && EXPECTED_LLM_PROVIDER_URLS.includes(host)) {
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
                    logger.info(`Location: ${location}`);
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
                }
            })().catch(() => {
                /* swallow logging errors so they never affect the main flow */
            });
            // Caller receives stream immediately
            return res;
        }) as typeof fetch;
    }
}
