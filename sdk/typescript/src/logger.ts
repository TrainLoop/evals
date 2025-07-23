type Level = "error" | "warn" | "info" | "debug";
const ORDER: Record<Level, number> = { error: 0, warn: 1, info: 2, debug: 3 };
const DEFAULT_LEVEL: Level = "warn";

export function createLogger(scope: string) {
  const env = (process.env.TRAINLOOP_LOG_LEVEL || DEFAULT_LEVEL).toLowerCase() as Level;
  const threshold = ORDER[env] ?? ORDER.info;

  function log(level: Level, msg: string): void {
    if (ORDER[level] > threshold) return;
    const ts = new Date().toISOString();
    // eslint-disable-next-line no-console
    console[level](`[${level.toUpperCase()}] [${ts}] [${scope}] ${msg}`);
  }

  return {
    error: (m: string) => log("error", m),
    warn: (m: string) => log("warn", m),
    info: (m: string) => log("info", m),
    debug: (m: string) => log("debug", m)
  };
}