import fs from "fs";
import yaml from "js-yaml";
import path from "path";
import { DEFAULT_HOST_ALLOWLIST } from "./constants";
import { TrainloopConfig } from "./types/shared";

export const loadConfig = () => {
    /**
     * Load TrainLoop configuration into environment variables.
     *
     * Priority order:
     * 1. Existing environment variables (highest priority)
     * 2. Config file values (fallback)
     * 3. Fail if critical variables are missing from both sources
     *
     * Config path resolution:
     * 1. TRAINLOOP_CONFIG_PATH environment variable
     * 2. Auto-discovery (trainloop/trainloop.config.yaml or ./trainloop.config.yaml)
     */
    // Check which environment variables are already set
    const dataFolderSet = !!process.env.TRAINLOOP_DATA_FOLDER;
    const hostAllowlistSet = !!process.env.TRAINLOOP_HOST_ALLOWLIST;
    const logLevelSet = !!process.env.TRAINLOOP_LOG_LEVEL;

    // Determine config path - prioritize env var, then auto-discovery
    const configPath = process.env.TRAINLOOP_CONFIG_PATH ??
        (fs.existsSync(path.join(process.cwd(), "trainloop/trainloop.config.yaml"))
            ? path.join(process.cwd(), "trainloop/trainloop.config.yaml")
            : path.join(process.cwd(), "trainloop.config.yaml"));

    // Try to load config file
    let configData: TrainloopConfig["trainloop"] | null = null;
    if (fs.existsSync(configPath)) {
        try {
            const config = yaml.load(fs.readFileSync(configPath, "utf8")) as TrainloopConfig;
            configData = config.trainloop;
            console.debug(`Loaded TrainLoop config from ${configPath}`);
        } catch (error) {
            console.warn(`Failed to load config file ${configPath}:`, error);
        }
    } else {
        console.debug(`TrainLoop config file not found at ${configPath}`);
    }

    // Track what we're using from config vs environment
    const configUsed: string[] = [];

    // Set environment variables, prioritizing existing values
    if (!dataFolderSet) {
        if (configData && configData.data_folder) {
            // Make data_folder path absolute if it's relative
            const dataFolder = configData.data_folder;
            const absoluteDataFolder = path.isAbsolute(dataFolder)
                ? dataFolder
                : path.resolve(path.dirname(configPath), dataFolder);
            process.env.TRAINLOOP_DATA_FOLDER = absoluteDataFolder;
            configUsed.push("data_folder");
        } else {
            console.warn(
                "TRAINLOOP_DATA_FOLDER not set in environment and not found in config file. " +
                "SDK will be disabled unless the variable is set."
            );
        }
    }

    if (!hostAllowlistSet) {
        if (configData && configData.host_allowlist) {
            process.env.TRAINLOOP_HOST_ALLOWLIST = configData.host_allowlist.join(",");
            configUsed.push("host_allowlist");
        } else {
            // Use default host allowlist if not set anywhere
            process.env.TRAINLOOP_HOST_ALLOWLIST = DEFAULT_HOST_ALLOWLIST.join(",");
        }
    }

    if (!logLevelSet) {
        if (configData && configData.log_level) {
            process.env.TRAINLOOP_LOG_LEVEL = configData.log_level.toUpperCase();
            configUsed.push("log_level");
        } else {
            // Use default log level if not set anywhere
            process.env.TRAINLOOP_LOG_LEVEL = "WARN";
        }
    }

    // Log summary of what was loaded
    if (configUsed.length > 0) {
        console.debug(`Using config values for: ${configUsed.join(", ")}`);
    }
    if (dataFolderSet || hostAllowlistSet || logLevelSet) {
        const envVars = [];
        if (dataFolderSet) envVars.push("data_folder");
        if (hostAllowlistSet) envVars.push("host_allowlist");
        if (logLevelSet) envVars.push("log_level");
        console.debug(`Using environment variables for: ${envVars.join(", ")}`);
    }
};
