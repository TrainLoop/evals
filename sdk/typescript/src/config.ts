import fs from "fs";
import yaml from "js-yaml";
import path from "path";
import { DEFAULT_HOST_ALLOWLIST } from "./constants";
import { TrainloopConfig } from "./types/shared";
import { createLogger } from "./logger";

const logger = createLogger("trainloop-config");

// Track which config file was last loaded to detect changes
let lastLoadedConfigPath: string | null = null;
let configSetEnvVars: Set<string> = new Set();

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
    logger.debug("Starting config load process");
    
    // Determine config path - prioritize env var, then auto-discovery
    logger.debug(`Config path resolution: TRAINLOOP_CONFIG_PATH=${process.env.TRAINLOOP_CONFIG_PATH || "(not set)"}`);
    logger.debug(`Current working directory: ${process.cwd()}`);
    
    const trainloopSubdirPath = path.join(process.cwd(), "trainloop/trainloop.config.yaml");
    const rootPath = path.join(process.cwd(), "trainloop.config.yaml");
    
    logger.debug(`Checking for config at: ${trainloopSubdirPath} - exists: ${fs.existsSync(trainloopSubdirPath)}`);
    logger.debug(`Checking for config at: ${rootPath} - exists: ${fs.existsSync(rootPath)}`);
    
    const configPath = process.env.TRAINLOOP_CONFIG_PATH ??
        (fs.existsSync(trainloopSubdirPath) ? trainloopSubdirPath : rootPath);
    
    logger.debug(`Selected config path: ${configPath}`);
    
    // Check if config path changed - if so, reset environment vars that were set by config
    if (lastLoadedConfigPath !== null && lastLoadedConfigPath !== configPath) {
        logger.debug(`Config path changed from ${lastLoadedConfigPath} to ${configPath}, resetting config-set env vars`);
        // Temporarily disable this feature to avoid potential infinite loops
        // for (const envVar of configSetEnvVars) {
        //     delete process.env[envVar];
        //     logger.debug(`Reset ${envVar}`);
        // }
        // configSetEnvVars.clear();
    }
    
    // Check which environment variables are already set (excluding those we set from config)
    const dataFolderSet = !!process.env.TRAINLOOP_DATA_FOLDER && !configSetEnvVars.has('TRAINLOOP_DATA_FOLDER');
    const hostAllowlistSet = !!process.env.TRAINLOOP_HOST_ALLOWLIST && !configSetEnvVars.has('TRAINLOOP_HOST_ALLOWLIST');
    const logLevelSet = !!process.env.TRAINLOOP_LOG_LEVEL && !configSetEnvVars.has('TRAINLOOP_LOG_LEVEL');
    
    logger.debug(`Environment variables already set: data_folder=${dataFolderSet}, host_allowlist=${hostAllowlistSet}, log_level=${logLevelSet}`);
    if (dataFolderSet) logger.debug(`  TRAINLOOP_DATA_FOLDER: ${process.env.TRAINLOOP_DATA_FOLDER}`);
    if (hostAllowlistSet) logger.debug(`  TRAINLOOP_HOST_ALLOWLIST: ${process.env.TRAINLOOP_HOST_ALLOWLIST}`);
    if (logLevelSet) logger.debug(`  TRAINLOOP_LOG_LEVEL: ${process.env.TRAINLOOP_LOG_LEVEL}`);

    // Try to load config file
    let configData: TrainloopConfig["trainloop"] | null = null;
    if (fs.existsSync(configPath)) {
        logger.debug(`Config file exists, attempting to load...`);
        try {
            const fileContent = fs.readFileSync(configPath, "utf8");
            logger.debug(`Config file size: ${fileContent.length} bytes`);
            
            const config = yaml.load(fileContent) as TrainloopConfig;
            configData = config.trainloop;
            
            logger.info(`Loaded TrainLoop config from ${configPath}`);
            logger.debug(`Config data: ${JSON.stringify(configData, null, 2)}`);
        } catch (error) {
            logger.error(`Failed to load config file ${configPath}: ${error}`);
            console.warn(`Failed to load config file ${configPath}:`, error);
        }
    } else {
        logger.warn(`TrainLoop config file not found at ${configPath}`);
        console.debug(`TrainLoop config file not found at ${configPath}`);
    }

    // Track what we're using from config vs environment
    const configUsed: string[] = [];

    // Set environment variables, prioritizing existing values
    if (!dataFolderSet) {
        logger.debug("TRAINLOOP_DATA_FOLDER not set, checking config...");
        if (configData && configData.data_folder) {
            // Make data_folder path absolute if it's relative
            const dataFolder = configData.data_folder;
            logger.debug(`Config data_folder: ${dataFolder}`);
            logger.debug(`Is absolute path: ${path.isAbsolute(dataFolder)}`);
            
            const absoluteDataFolder = path.isAbsolute(dataFolder)
                ? dataFolder
                : path.resolve(path.dirname(configPath), dataFolder);
            
            logger.debug(`Resolved data_folder to: ${absoluteDataFolder}`);
            process.env.TRAINLOOP_DATA_FOLDER = absoluteDataFolder;
            configUsed.push("data_folder");
            configSetEnvVars.add("TRAINLOOP_DATA_FOLDER");
        } else {
            logger.warn("TRAINLOOP_DATA_FOLDER not set in environment and not found in config file");
            console.warn(
                "TRAINLOOP_DATA_FOLDER not set in environment and not found in config file. " +
                "SDK will be disabled unless the variable is set."
            );
        }
    } else {
        logger.debug(`Using existing TRAINLOOP_DATA_FOLDER: ${process.env.TRAINLOOP_DATA_FOLDER}`);
    }

    if (!hostAllowlistSet) {
        logger.debug("TRAINLOOP_HOST_ALLOWLIST not set, checking config...");
        if (configData && configData.host_allowlist) {
            const allowlist = configData.host_allowlist.join(",");
            logger.debug(`Setting host_allowlist from config: ${allowlist}`);
            process.env.TRAINLOOP_HOST_ALLOWLIST = allowlist;
            configUsed.push("host_allowlist");
            configSetEnvVars.add("TRAINLOOP_HOST_ALLOWLIST");
        } else {
            // Use default host allowlist if not set anywhere
            const defaultList = DEFAULT_HOST_ALLOWLIST.join(",");
            logger.debug(`Using default host_allowlist: ${defaultList}`);
            process.env.TRAINLOOP_HOST_ALLOWLIST = defaultList;
        }
    } else {
        logger.debug(`Using existing TRAINLOOP_HOST_ALLOWLIST: ${process.env.TRAINLOOP_HOST_ALLOWLIST}`);
    }

    if (!logLevelSet) {
        logger.debug("TRAINLOOP_LOG_LEVEL not set, checking config...");
        if (configData && configData.log_level) {
            const level = configData.log_level.toUpperCase();
            logger.debug(`Setting log_level from config: ${level}`);
            process.env.TRAINLOOP_LOG_LEVEL = level;
            configUsed.push("log_level");
            configSetEnvVars.add("TRAINLOOP_LOG_LEVEL");
        } else {
            // Use default log level if not set anywhere
            logger.debug("Using default log_level: WARN");
            process.env.TRAINLOOP_LOG_LEVEL = "WARN";
        }
    } else {
        logger.debug(`Using existing TRAINLOOP_LOG_LEVEL: ${process.env.TRAINLOOP_LOG_LEVEL}`);
    }

    // Log summary of what was loaded
    logger.debug("Config loading complete. Final state:");
    logger.debug(`  TRAINLOOP_DATA_FOLDER: ${process.env.TRAINLOOP_DATA_FOLDER || "(not set)"}`);
    logger.debug(`  TRAINLOOP_HOST_ALLOWLIST: ${process.env.TRAINLOOP_HOST_ALLOWLIST || "(not set)"}`);
    logger.debug(`  TRAINLOOP_LOG_LEVEL: ${process.env.TRAINLOOP_LOG_LEVEL || "(not set)"}`);
    
    if (configUsed.length > 0) {
        logger.info(`Using config values for: ${configUsed.join(", ")}`);
        console.debug(`Using config values for: ${configUsed.join(", ")}`);
    }
    if (dataFolderSet || hostAllowlistSet || logLevelSet) {
        const envVars = [];
        if (dataFolderSet) envVars.push("data_folder");
        if (hostAllowlistSet) envVars.push("host_allowlist");
        if (logLevelSet) envVars.push("log_level");
        logger.info(`Using environment variables for: ${envVars.join(", ")}`);
        console.debug(`Using environment variables for: ${envVars.join(", ")}`);
    }
    
    // Remember this config path for next time
    lastLoadedConfigPath = configPath;
};
