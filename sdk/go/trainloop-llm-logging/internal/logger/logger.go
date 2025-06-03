package logger

import (
	"fmt"
	"log"
	"os"
	"strings"
	"time"
)

// LogLevel defines the severity of a log message.
type LogLevel int

const (
	// DEBUG level
	DEBUG LogLevel = iota
	// INFO level
	INFO
	// WARN level
	WARN
	// ERROR level
	ERROR
)

var logLevelNames = map[LogLevel]string{
	DEBUG: "DEBUG",
	INFO:  "INFO",
	WARN:  "WARN",
	ERROR: "ERROR",
}

var currentLogLevel = WARN // Default log level

// Logger is a simple logger instance.
type Logger struct {
	scope string
}

func init() {
	SetLogLevel(os.Getenv("TRAINLOOP_LOG_LEVEL"))
}

// SetLogLevel sets the global logging level.
func SetLogLevel(levelStr string) {
	levelStr = strings.ToUpper(levelStr)
	switch levelStr {
	case "DEBUG":
		currentLogLevel = DEBUG
	case "INFO":
		currentLogLevel = INFO
	case "WARN":
		currentLogLevel = WARN
	case "ERROR":
		currentLogLevel = ERROR
	default:
		if levelStr != "" {
			log.Printf("[WARN] [logger] Invalid TRAINLOOP_LOG_LEVEL '%s', defaulting to WARN\n", levelStr)
		}
		currentLogLevel = WARN // Default if invalid or not set
	}
}

// CreateLogger creates a new logger with a given scope.
func CreateLogger(scope string) *Logger {
	return &Logger{scope: scope}
}

func (l *Logger) log(level LogLevel, format string, args ...any) {
	if level < currentLogLevel {
		return
	}
	timestamp := time.Now().Format("2006-01-02T15:04:05Z07:00")
	prefix := fmt.Sprintf("[%s] [%s] [%s] ", logLevelNames[level], timestamp, l.scope)
	log.Printf(prefix+format+"\n", args...)
}

// Debug logs a message at DEBUG level.
func (l *Logger) Debug(format string, args ...any) {
	l.log(DEBUG, format, args...)
}

// Info logs a message at INFO level.
func (l *Logger) Info(format string, args ...any) {
	l.log(INFO, format, args...)
}

// Warn logs a message at WARN level.
func (l *Logger) Warn(format string, args ...any) {
	l.log(WARN, format, args...)
}

// Error logs a message at ERROR level.
func (l *Logger) Error(format string, args ...any) {
	l.log(ERROR, format, args...)
}
