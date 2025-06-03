package config

import (
	"os"
	"path/filepath"
	"strings"

	"github.com/trainloop/sdk/go/trainloop-llm-logging/internal/logger"
	"github.com/trainloop/sdk/go/trainloop-llm-logging/internal/types"

	"gopkg.in/yaml.v3"
)

var log = logger.CreateLogger("trainloop-config")

// DefaultHostAllowlist is the default list of hosts to monitor.
var DefaultHostAllowlist = []string{"api.openai.com", "api.anthropic.com"}

const configFileName = "trainloop.config.yaml"

func resolveDataFolderPath(dataFolder string, configPath string, rootDir string) string {
	if dataFolder == "" {
		return ""
	}
	if filepath.IsAbs(dataFolder) {
		return dataFolder
	}
	if configPath != "" {
		return filepath.Join(filepath.Dir(configPath), dataFolder)
	}
	return filepath.Join(rootDir, dataFolder)
}

// LoadConfigIntoEnv loads configuration from YAML file or environment variables.
// Priority: Environment variables > YAML file > Defaults.
// It sets environment variables if they are not already set.
func LoadConfigIntoEnv(trainloopConfigPathOpt string) {
	dataFolderSet := os.Getenv("TRAINLOOP_DATA_FOLDER") != ""
	hostAllowlistSet := os.Getenv("TRAINLOOP_HOST_ALLOWLIST") != ""
	logLevelSet := os.Getenv("TRAINLOOP_LOG_LEVEL") != ""

	if dataFolderSet && hostAllowlistSet && logLevelSet {
		log.Debug("All TrainLoop environment variables already set, skipping config file")
		return
	}

	rootDir, err := os.Getwd()
	if err != nil {
		log.Warn("Failed to get current working directory: %v", err)
		rootDir = "." // Fallback
	}

	var resolvedConfigPath string
	configPathSource := trainloopConfigPathOpt
	if configPathSource == "" {
		configPathSource = os.Getenv("TRAINLOOP_CONFIG_PATH")
	}

	if configPathSource != "" {
		path := configPathSource
		if filepath.IsAbs(path) {
			info, err := os.Stat(path)
			if err == nil && info.IsDir() {
				resolvedConfigPath = filepath.Join(path, configFileName)
			} else {
				resolvedConfigPath = path
			}
		} else {
			absPath, _ := filepath.Abs(filepath.Join(rootDir, path))
			info, err := os.Stat(absPath)
			if err == nil && info.IsDir() {
				resolvedConfigPath = filepath.Join(absPath, configFileName)
			} else {
				resolvedConfigPath = absPath
			}
		}
	} else {
		// Auto-discovery
		trainloopDir := filepath.Join(rootDir, "trainloop")
		if info, err := os.Stat(trainloopDir); err == nil && info.IsDir() {
			resolvedConfigPath = filepath.Join(trainloopDir, configFileName)
		} else {
			resolvedConfigPath = filepath.Join(rootDir, configFileName)
		}
	}

	var configData types.TrainloopConfigObject
	if _, err := os.Stat(resolvedConfigPath); err == nil {
		yamlFile, err := os.ReadFile(resolvedConfigPath)
		if err != nil {
			log.Warn("Failed to read config file %s: %v", resolvedConfigPath, err)
		} else {
			var fullConfig types.TrainloopConfig
			err = yaml.Unmarshal(yamlFile, &fullConfig)
			if err != nil {
				log.Warn("Failed to parse config file %s: %v", resolvedConfigPath, err)
			} else {
				configData = fullConfig.Trainloop
				log.Debug("Loaded TrainLoop config from %s", resolvedConfigPath)
			}
		}
	} else {
		log.Debug("TrainLoop config file not found at %s", resolvedConfigPath)
	}

	// Set TRAINLOOP_DATA_FOLDER
	if !dataFolderSet {
		if configData.DataFolder != "" {
			resolvedPath := resolveDataFolderPath(configData.DataFolder, resolvedConfigPath, rootDir)
			os.Setenv("TRAINLOOP_DATA_FOLDER", resolvedPath)
		} else {
			// This is a critical variable, but we allow SDK to be disabled if not set.
			// The main `Collect` function will check for this.
			log.Info("TRAINLOOP_DATA_FOLDER not set in environment or config file.")
		}
	}

	// Set TRAINLOOP_HOST_ALLOWLIST
	if !hostAllowlistSet {
		if len(configData.HostAllowlist) > 0 {
			os.Setenv("TRAINLOOP_HOST_ALLOWLIST", strings.Join(configData.HostAllowlist, ","))
		} else {
			os.Setenv("TRAINLOOP_HOST_ALLOWLIST", strings.Join(DefaultHostAllowlist, ","))
		}
	}
	// Ensure TRAINLOOP_HOST_ALLOWLIST is set if still empty (e.g. if default was an empty list)
	if os.Getenv("TRAINLOOP_HOST_ALLOWLIST") == "" {
		os.Setenv("TRAINLOOP_HOST_ALLOWLIST", strings.Join(DefaultHostAllowlist, ","))
	}

	// Set TRAINLOOP_LOG_LEVEL
	if !logLevelSet {
		if configData.LogLevel != "" {
			os.Setenv("TRAINLOOP_LOG_LEVEL", strings.ToUpper(configData.LogLevel))
		} else {
			os.Setenv("TRAINLOOP_LOG_LEVEL", "WARN") // Default log level
		}
	}
	logger.SetLogLevel(os.Getenv("TRAINLOOP_LOG_LEVEL")) // Re-apply log level
}

// GetHostAllowlist returns the current host allowlist from environment variables.
func GetHostAllowlist() []string {
	hosts := os.Getenv("TRAINLOOP_HOST_ALLOWLIST")
	if hosts == "" {
		return DefaultHostAllowlist
	}
	return strings.Split(hosts, ",")
}
