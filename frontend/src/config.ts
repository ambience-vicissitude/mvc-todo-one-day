/**
 * Build-time settings. The default relative URL keeps one image valid in every environment.
 */

/**
 * Base URL for the API endpoints.
 *
 * @type {string}
 */
export const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? '/api';

/**
 * Logging level for the application.
 *
 * @type {string}
 */
export const LOG_LEVEL: string = import.meta.env.VITE_LOG_LEVEL ?? 'info';
