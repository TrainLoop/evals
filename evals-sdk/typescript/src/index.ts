import { patchHttp } from "./instrumentation/http";
import http from "http";
import https from "https";
import { patchFetch } from "./instrumentation/fetch";
import { FileExporter } from "./exporter"
import path from "path";
import fs from "fs";
import yaml from "js-yaml";
import { TrainloopConfig } from "./types/shared";
/**
 * Public surface:
 *  • HEADER_NAME      - constant header string
 *  • trainloopTag(tag)   - helper to add the trainloop tag to the header
 *  • installHooks()   - manual bootstrap (rarely needed)
 */

export const HEADER_NAME = "X-Trainloop-Tag";

/**
 * Convenience helper - merge into your fetch/OpenAI headers
 */
export function trainloopTag(tag: string): Record<string, string> {
  return { [HEADER_NAME]: tag };
}

const loadConfig = () => {
  // Assume the trainloop config is in the project root
  const configPath = process.env.TRAINLOOP_CONFIG_PATH ?? path.join(process.cwd(), "trainloop/trainloop.config.yaml");
  if (!fs.existsSync(configPath)) {
    console.info(`No config found at ${configPath}. Please add a TRAINLOOP_CONFIG_PATH env var or run this command near the trainloop/ directory. Data is not being collected.`);
    return;
  }
  const config = yaml.load(fs.readFileSync(configPath, "utf8")) as TrainloopConfig;

  console.info(`TrainLoop config loaded from ${configPath}`);

  // Make data_folder path absolute if it's relative
  const dataFolder = config.trainloop.data_folder;
  const absoluteDataFolder = path.isAbsolute(dataFolder)
    ? dataFolder
    : path.resolve(path.dirname(configPath), dataFolder);

  process.env.TRAINLOOP_DATA_FOLDER = absoluteDataFolder;
  process.env.TRAINLOOP_HOST_ALLOWLIST = config.trainloop.host_allowlist.join(",");
  process.env.TRAINLOOP_LOG_LEVEL = config.trainloop.log_level;
}

const init = async () => {
  // First load the config from the trainloop folder if available
  loadConfig();
  await import("./instrumentation");
  const exporter = new FileExporter();
  patchHttp(http, exporter);
  patchHttp(https, exporter);
  patchFetch(exporter);
}

init();

const DEFAULT_ALLOWLIST = "api.openai.com,api.anthropic.com";

// host allow‑list
export const EXPECTED_LLM_PROVIDER_URLS = (process.env.TRAINLOOP_HOST_ALLOWLIST ?? DEFAULT_ALLOWLIST)
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);
