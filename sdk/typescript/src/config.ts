import fs from "fs";
import yaml from "js-yaml";
import path from "path";
import { DEFAULT_HOST_ALLOWLIST } from "./constants";
import { TrainloopConfig } from "./types/shared";
import { createLogger } from "./logger";

// Track which config file was last loaded to detect changes
let lastLoadedConfigPath: string | null = null;
let configSetEnvVars: Set<string> = new Set();
let configSetValues: Map<string, string> = new Map(); // Track values set by config

/**
 * Reset config state - used for testing
 * @internal
 */
export const resetConfigState = (): void => {
    lastLoadedConfigPath = null;
    configSetEnvVars.clear();
    configSetValues.clear();
};

export const loadConfig = (): void => {
    const logger = createLogger("trainloop-config");
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
    
    // Check if config path changed - if so, reset environment vars that were set by config
    if (lastLoadedConfigPath !== null && lastLoadedConfigPath !== configPath) {
        logger.debug(`Config path changed from ${lastLoadedConfigPath} to ${configPath}, resetting config tracking`);
        
        // Clear environment variables that were set by config and haven't been modified by user
        for (const envVar of configSetEnvVars) {
            const configValue = configSetValues.get(envVar);
            const currentValue = process.env[envVar];
            if (configValue !== undefined && currentValue === configValue) {
                // Value hasn't been changed by user, safe to clear
                delete process.env[envVar];
                logger.debug(`Cleared config-set env var: ${envVar} (was: ${configValue})`);
            } else {
                logger.debug(`Preserving user-modified env var: ${envVar} (config: ${configValue}, current: ${currentValue})`);
            }
        }
        
        // Clear internal tracking so subsequent config loads can reapply as needed
        configSetEnvVars.clear();
        configSetValues.clear();
    }
    
    // Check which environment variables are already set (excluding those we set from config)
    const dataFolderSet = !!process.env.TRAINLOOP_DATA_FOLDER && !configSetEnvVars.has('TRAINLOOP_DATA_FOLDER');
    const hostAllowlistSet = !!process.env.TRAINLOOP_HOST_ALLOWLIST &&
        !configSetEnvVars.has('TRAINLOOP_HOST_ALLOWLIST') &&
        process.env.TRAINLOOP_HOST_ALLOWLIST !== DEFAULT_HOST_ALLOWLIST.join(',');

    logger.debug(`Host allowlist check: value="${process.env.TRAINLOOP_HOST_ALLOWLIST}", tracked=${configSetEnvVars.has('TRAINLOOP_HOST_ALLOWLIST')}, default="${DEFAULT_HOST_ALLOWLIST.join(',')}", set=${hostAllowlistSet}`);
    
    const logLevelSet = !!process.env.TRAINLOOP_LOG_LEVEL &&
        !configSetEnvVars.has('TRAINLOOP_LOG_LEVEL');
    const flushImmediatelySet = !!process.env.TRAINLOOP_FLUSH_IMMEDIATELY &&
        !configSetEnvVars.has('TRAINLOOP_FLUSH_IMMEDIATELY');
    
    logger.debug(`Environment variables already set: data_folder=${dataFolderSet}, host_allowlist=${hostAllowlistSet}, log_level=${logLevelSet}, flush_immediately=${flushImmediatelySet}`);
    
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
            configSetValues.set("TRAINLOOP_DATA_FOLDER", absoluteDataFolder); // Track value
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
            configSetValues.set("TRAINLOOP_HOST_ALLOWLIST", allowlist); // Track value
        } else {
            // Use default host allowlist if not set anywhere
            const defaultList = DEFAULT_HOST_ALLOWLIST.join(",");
            logger.debug(`Using default host_allowlist: ${defaultList}`);
            process.env.TRAINLOOP_HOST_ALLOWLIST = defaultList;
            configSetEnvVars.add("TRAINLOOP_HOST_ALLOWLIST");
            configSetValues.set("TRAINLOOP_HOST_ALLOWLIST", defaultList); // Track value
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
            configSetValues.set("TRAINLOOP_LOG_LEVEL", level); // Track value
        } else {
            // Use default log level if not set anywhere
            logger.debug("Using default log_level: WARN");
            process.env.TRAINLOOP_LOG_LEVEL = "WARN";
            configSetEnvVars.add("TRAINLOOP_LOG_LEVEL");
            configSetValues.set("TRAINLOOP_LOG_LEVEL", "WARN"); // Track value
        }
    } else {
        logger.debug(`Using existing TRAINLOOP_LOG_LEVEL: ${process.env.TRAINLOOP_LOG_LEVEL}`);
    }

    if (!flushImmediatelySet) {
        logger.debug("TRAINLOOP_FLUSH_IMMEDIATELY not set, checking config...");
        let flushVal = "true";
        if (configData && typeof configData.flush_immediately === 'boolean') {
            flushVal = String(configData.flush_immediately);
        }
        logger.debug(`Setting flush_immediately: ${flushVal}`);
        process.env.TRAINLOOP_FLUSH_IMMEDIATELY = flushVal;
        configUsed.push("flush_immediately");
        configSetEnvVars.add("TRAINLOOP_FLUSH_IMMEDIATELY");
        configSetValues.set("TRAINLOOP_FLUSH_IMMEDIATELY", flushVal);
    } else {
        logger.debug(`Using existing TRAINLOOP_FLUSH_IMMEDIATELY: ${process.env.TRAINLOOP_FLUSH_IMMEDIATELY}`);
    }

    // Log summary of what was loaded
    logger.debug("Config loading complete. Final state:");
    logger.debug(`  TRAINLOOP_DATA_FOLDER: ${process.env.TRAINLOOP_DATA_FOLDER || "(not set)"}`);
    logger.debug(`  TRAINLOOP_HOST_ALLOWLIST: ${process.env.TRAINLOOP_HOST_ALLOWLIST || "(not set)"}`);
    logger.debug(`  TRAINLOOP_LOG_LEVEL: ${process.env.TRAINLOOP_LOG_LEVEL || "(not set)"}`);
    logger.debug(`  TRAINLOOP_FLUSH_IMMEDIATELY: ${process.env.TRAINLOOP_FLUSH_IMMEDIATELY || "(not set)"}`);
    
    if (configUsed.length > 0) {
        logger.info(`Using config values for: ${configUsed.join(", ")}`);
        console.debug(`Using config values for: ${configUsed.join(", ")}`);
    }
    if (dataFolderSet || hostAllowlistSet || logLevelSet || flushImmediatelySet) {
        const envVars = [];
        if (dataFolderSet) envVars.push("data_folder");
        if (hostAllowlistSet) envVars.push("host_allowlist");
        if (logLevelSet) envVars.push("log_level");
        if (flushImmediatelySet) envVars.push("flush_immediately");
        logger.info(`Using environment variables for: ${envVars.join(", ")}`);
        console.debug(`Using environment variables for: ${envVars.join(", ")}`);
    }
    
    // Remember this config path for next time
    lastLoadedConfigPath = configPath;
};
