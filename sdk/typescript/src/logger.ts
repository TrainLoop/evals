type Level = "error" | "warn" | "info" | "debug";
const ORDER: Record<Level, number> = { error: 0, warn: 1, info: 2, debug: 3 };
const DEFAULT_LEVEL: Level = "warn";

interface Logger {
  error: (m: string) => void;
  warn: (m: string) => void;
  info: (m: string) => void;
  debug: (m: string) => void;
}

export function createLogger(scope: string): Logger {
  let logger: Logger | null = null;
  let cachedLogLevel: string | undefined = undefined;

  function getLogger(): Logger {
    const currentLogLevel = process.env.TRAINLOOP_LOG_LEVEL;
    
    // Invalidate cached logger if log level changed
    if (!logger || cachedLogLevel !== currentLogLevel) {
      cachedLogLevel = currentLogLevel;
      const env = (currentLogLevel || DEFAULT_LEVEL).toLowerCase() as Level;
      const threshold = ORDER[env] ?? ORDER.info;

      function log(level: Level, msg: string): void {
        if (ORDER[level] > threshold) return;
        const ts = new Date().toISOString();
        // eslint-disable-next-line no-console
        console[level](`[${level.toUpperCase()}] [${ts}] [${scope}] ${msg}`);
      }

      logger = {
        error: (m: string) => log("error", m),
        warn: (m: string) => log("warn", m),
        info: (m: string) => log("info", m),
        debug: (m: string) => log("debug", m)
      };
    }
    return logger;
  }

  // Return a proxy that creates logger on first access
  return new Proxy({} as Logger, {
    get(_target, prop: keyof Logger) {
      return getLogger()[prop];
    }
  });
}