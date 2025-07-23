import { FileStorage } from "@flystorage/file-storage";
import { LocalStorageAdapter } from "@flystorage/local-fs";
import { AwsS3StorageAdapter } from "@flystorage/aws-s3";
import { GoogleCloudStorageAdapter } from "@flystorage/google-cloud-storage";
import { S3Client } from "@aws-sdk/client-s3";
import { Storage as GCS } from "@google-cloud/storage";
import { resolve } from "node:path";
import { createLogger } from "./logger";
import {
  CollectedSample,
  LLMCallLocation,
  Registry,
  RegistryEntry,
} from "./types/shared";

const logger = createLogger("trainloop-storage");

interface S3Config {
  bucket: string;
  prefix?: string;
}

interface GCSConfig {
  bucket: string;
  prefix?: string;
}

function parseS3(path: string): S3Config {
  const url = new URL(path);
  const bucket = url.hostname;
  const prefix = url.pathname.slice(1); // Remove leading slash
  return { bucket, prefix: prefix || undefined };
}

function parseGCS(path: string): GCSConfig {
  const url = new URL(path);
  const bucket = url.hostname;
  const prefix = url.pathname.slice(1); // Remove leading slash
  return { bucket, prefix: prefix || undefined };
}

function storageFor(path: string): FileStorage {
  if (path.startsWith("s3://")) {
    const { bucket, prefix } = parseS3(path);
    logger.debug(
      `Creating S3 storage for bucket: ${bucket}, prefix: ${prefix || "(none)"}`
    );
    return new FileStorage(
      new AwsS3StorageAdapter(new S3Client(), { bucket, prefix })
    );
  }
  if (path.startsWith("gs://") || path.startsWith("gcp://")) {
    const { bucket, prefix } = parseGCS(path);
    logger.debug(
      `Creating GCS storage for bucket: ${bucket}, prefix: ${
        prefix || "(none)"
      }`
    );
    return new FileStorage(
      new GoogleCloudStorageAdapter(new GCS().bucket(bucket), { prefix })
    );
  }
  // local
  logger.debug(`Creating local storage for path: ${path}`);
  return new FileStorage(new LocalStorageAdapter(resolve(path)));
}

function _nowIso(): string {
  return new Date().toISOString();
}

export async function updateRegistry(
  dataDir: string,
  loc: LLMCallLocation,
  tag: string
): Promise<void> {
  logger.debug(
    `Updating registry: dataDir=${dataDir}, location=${JSON.stringify(
      loc
    )}, tag=${tag}`
  );

  const store = storageFor(dataDir);
  const registryKey = "_registry.json";

  let reg: Registry;

  try {
    // Try to read existing registry
    if (await store.fileExists(registryKey)) {
      logger.debug(`Reading existing registry from ${registryKey}`);
      const content = await store.read(registryKey);
      // If content is a Buffer or Readable, convert to string
      let contentStr: string;
      if (typeof content === "string") {
        contentStr = content;
      } else if (Buffer.isBuffer(content)) {
        contentStr = content.toString("utf-8");
      } else if (content && typeof (content as any).read === "function") {
        // Node.js Readable stream
        contentStr = await new Promise<string>((resolve, reject) => {
          let data = "";
          (content as NodeJS.ReadableStream).setEncoding("utf-8");
          (content as NodeJS.ReadableStream).on(
            "data",
            (chunk) => (data += chunk)
          );
          (content as NodeJS.ReadableStream).on("end", () => resolve(data));
          (content as NodeJS.ReadableStream).on("error", reject);
        });
      } else {
        throw new Error("Unsupported content type returned from store.read");
      }
      reg = JSON.parse(contentStr);

      // Ensure reg has the expected structure
      if (!reg || typeof reg !== "object") {
        reg = { schema: 1, files: {} };
      }

      // Ensure files property exists
      if (!reg.files) {
        reg.files = {};
      }
    } else {
      logger.debug("Creating new registry");
      reg = { schema: 1, files: {} };
    }
  } catch (error) {
    logger.error(`Failed to load registry, creating new one: ${error}`);
    reg = { schema: 1, files: {} };
  }

  // Safely handle the location and file properties
  if (!loc) {
    logger.error("Location is undefined, using default");
    loc = { file: "unknown-file", lineNumber: "0" };
  }

  const fileName = loc.file || "unknown-file";

  // Safely initialize the file block
  if (!reg.files[fileName]) {
    logger.debug(`Creating new file block for ${fileName}`);
    reg.files[fileName] = {};
  }

  const fileBlock = reg.files[fileName];
  const now = _nowIso();
  const lineNumber = loc.lineNumber || "0";

  const entry = fileBlock[lineNumber];
  if (entry) {
    // Update existing entry
    logger.debug(`Updating existing entry for ${fileName}:${lineNumber}`);
    entry.tag = tag;
    entry.lineNumber = lineNumber;
    entry.lastSeen = now;
    entry.count++;
  } else {
    // Create new entry
    logger.debug(`Creating new entry for ${fileName}:${lineNumber}`);
    fileBlock[lineNumber] = {
      lineNumber: lineNumber,
      tag,
      firstSeen: now,
      lastSeen: now,
      count: 1,
    };
  }

  // Write the updated registry
  try {
    logger.debug(`Writing registry to: ${registryKey}`);
    await store.write(registryKey, JSON.stringify(reg, null, 2), {
      visibility: "private",
    });
    logger.debug(`Registry updated → ${fileName}:${lineNumber} (${tag})`);
  } catch (error) {
    logger.error(`Failed to update registry: ${error}`);
    throw error;
  }
}

export async function saveSamples(
  dataDir: string,
  samples: CollectedSample[]
): Promise<void> {
  if (samples.length === 0) {
    logger.debug("No samples to save");
    return;
  }

  logger.debug(`Saving ${samples.length} samples to ${dataDir}`);

  const store = storageFor(dataDir);
  const windowTime = 10 * 60 * 1000; // 10 minutes
  let targetTimestamp = Date.now();

  try {
    if (
      !dataDir.startsWith("s3://") &&
      !dataDir.startsWith("gs://") &&
      !dataDir.startsWith("gcp://")
    ) {
      try {
        logger.debug("Using current timestamp for file naming");
      } catch (e) {
        logger.warn(`Error checking for recent event files: ${e}`);
      }
    }
  } catch (error) {
    logger.warn(`Error during timestamp resolution: ${error}`);
  }

  const lines = samples.map((s) => JSON.stringify(s));
  const eventKey = `events/${targetTimestamp}.jsonl`;

  try {
    logger.debug(`Writing ${lines.length} lines to ${eventKey}`);

    // Check if file exists and append, or create new file
    let existingContent = "";
    if (await store.fileExists(eventKey)) {
      const content = await store.read(eventKey);
      if (typeof content === "string") {
        existingContent = content;
      } else if (Buffer.isBuffer(content)) {
        existingContent = content.toString("utf-8");
      } else if (content && typeof (content as any).read === "function") {
        // Node.js Readable stream
        existingContent = await new Promise<string>((resolve, reject) => {
          let data = "";
          (content as NodeJS.ReadableStream).setEncoding("utf-8");
          (content as NodeJS.ReadableStream).on(
            "data",
            (chunk) => (data += chunk)
          );
          (content as NodeJS.ReadableStream).on("end", () => resolve(data));
          (content as NodeJS.ReadableStream).on("error", reject);
        });
      } else {
        throw new Error("Unsupported content type returned from store.read");
      }
    }

    const newContent = existingContent + lines.join("\n") + "\n";
    await store.write(eventKey, newContent, { visibility: "private" });

    logger.info(`Successfully saved ${samples.length} samples to ${eventKey}`);
  } catch (error) {
    logger.error(`Failed to save samples: ${error}`);
    throw error;
  }
}

export function updateRegistrySync(
  dataDir: string,
  location: LLMCallLocation,
  tag: string
): void {
  updateRegistry(dataDir, location, tag).catch((error) => {
    logger.error(`Failed to update registry synchronously: ${error}`);
  });
}

export function saveSamplesSync(
  dataDir: string,
  samples: CollectedSample[]
): void {
  saveSamples(dataDir, samples).catch((error) => {
    logger.error(`Failed to save samples synchronously: ${error}`);
  });
}
