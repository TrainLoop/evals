import http, { ClientRequest, IncomingMessage } from "node:http";
import https from "node:https";
import { PassThrough } from "node:stream";
import { EXPECTED_LLM_PROVIDER_URLS } from "../index";
import { FileExporter } from "../exporter";
import { getCallerSite, getCallerStack, getAndRemoveHeader, fullUrl, drain, formatStreamedContent, reqBodies } from "./utils";
import { HEADER_NAME } from "../index";
import { createLogger } from "../logger";

const logger = createLogger("trainloop-http");

/* ------------- patch http / https ------------- */

function getHost(opts: any): string | undefined {
    if (typeof opts === "string") {
        try {
            return new URL(opts).hostname;
        } catch {
            return undefined;
        }
    }
    return opts.host ?? opts.hostname;
}

export function patchHttp(mod: typeof http | typeof https, exporter: FileExporter): void {
    const orig = mod.request.bind(mod) as (...args: any[]) => ClientRequest;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    function patchedRequest(...args: any[]): ClientRequest {
        /* figure out user callback, if any (last arg that’s a function) */
        const userCb =
            typeof args[args.length - 1] === "function"
                ? (args.pop() as (res: IncomingMessage) => void)
                : undefined;
        const opts = args[0];
        const t0 = Date.now();

        // Remove and retrieve the X-Trainloop-Tag header
        let tagValue: string | undefined;
        if (opts && opts.headers) {
            tagValue = getAndRemoveHeader(opts.headers, HEADER_NAME);
        }

        const location = getCallerSite(getCallerStack());

        const req = orig(...args, (res: IncomingMessage) => {
            // We need a clone of the original response to avoid interfering with userCb
            const resClone = res.pipe(new PassThrough());

            // Process the clone for logging
            drain(resClone).then((body) => {
                const reqBody = (
                    reqBodies.get(req) ?? Buffer.alloc(0)
                ).toString("utf8");
                const t1 = Date.now();
                const ms = t1 - t0;
                const host = getHost(opts);

                if (host && EXPECTED_LLM_PROVIDER_URLS.includes(host)) {
                    // Format the response body if it's a streaming response
                    const formattedBody = formatStreamedContent(body);

                    logger.info("------- START HTTP CALL -------")
                    logger.info(`Method: ${req.method}`)
                    logger.info(`Resource: ${fullUrl(opts)}`)
                    logger.info(`Trainloop Tag: ${tagValue}`)
                    logger.info(`Request Body: ${reqBody || "(empty)"}`)
                    logger.info(`Status: ${res.statusCode}`)
                    logger.info(`Response Body: ${formattedBody}`)
                    logger.info(`Duration: ${ms}`)
                    logger.info("------- END HTTP CALL -------")

                    exporter.recordLLMCall({
                        requestBodyStr: reqBody,
                        responseBodyStr: formattedBody,
                        durationMs: Math.round(ms),
                        url: fullUrl(opts),
                        endTimeMs: Math.round(t1),
                        startTimeMs: Math.round(t0),
                        isLLMRequest: true,
                        location,
                        status: res.statusCode,
                        tag: tagValue,
                    })
                }
            });
            userCb?.(res);
        });

        /* tap .write() */
        const originalWrite = req.write;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        req.write = function (chunk: any, enc?: any, cb?: any): boolean {
            const buf = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk, enc);
            const prev = reqBodies.get(req) ?? Buffer.alloc(0);
            reqBodies.set(req, Buffer.concat([prev, buf]));
            return originalWrite.call(this, chunk, enc, cb);
        };

        return req;
    }

    // preserve public type surface
    (mod.request as typeof patchedRequest) = patchedRequest;
}