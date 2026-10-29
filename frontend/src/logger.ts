/**
 * Logger utility for the application.
 */


import { LOG_LEVEL } from './config';


/**
 * Logging levels used in the application.
 *
 * @type {{ readonly debug: 0; readonly info: 1; readonly warn: 2; readonly error: 3; }}
 */
const LEVELS = { debug: 0, info: 1, warn: 2, error: 3 } as const;
type Level = keyof typeof LEVELS;

const threshold = LEVELS[LOG_LEVEL as Level] ?? LEVELS.info;


/**
 * Logs a message at the specified level.
 *
 * @param {Level} level 
 * @param {string} message 
 */
function log(level: Level, message: string): void {
  if (LEVELS[level] >= threshold) {
    console[level](`${new Date().toISOString()} ${level.toUpperCase()} ${message}`);
  }
}

/**
 * Logger instance providing methods for different logging levels.
 * 
 * TRIM: Swap the console for a remote sink (e.g. an OpenTelemetry exporter, Grafana, etc.) here without touching callers.
 *
 * @type {{
 *  debug: (message: string) => void;
 *  info: (message: string) => void;
 *  warn: (message: string) => void;
 *  error: (message: string) => void;
 * }}
 */
export const logger = {
  debug: (message: string) => log('debug', message),
  info: (message: string) => log('info', message),
  warn: (message: string) => log('warn', message),
  error: (message: string) => log('error', message),
};
