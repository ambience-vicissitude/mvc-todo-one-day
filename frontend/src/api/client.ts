/**
 * API client utilities for the application.
 */

import { API_BASE_URL } from '../config';
import { logger } from '../logger';


/**
 * Represents an error returned by the API with an HTTP status code and message.
 *
 * @export
 * @class ApiError
 * @typedef {ApiError}
 * @extends {Error}
 */
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}


/**
 * Extracts a human-readable error message from an unknown error object.
 *
 * @export
 * @param {unknown} error 
 * @returns {string} 
 */
export function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Unexpected error';
}


/**
 * Reads the error detail from the response body, falling back to the status text if necessary.
 *
 * @async
 * @param {Response} response 
 * @returns {Promise<string>} 
 */
async function readDetail(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body.detail === 'string') return body.detail;
    if (Array.isArray(body.detail) && body.detail[0]?.msg) return body.detail[0].msg;
  } catch {
    // Non-JSON error body: fall through to the status text.
    logger.warn(`Failed to read error detail from response body`);
  }
  return response.statusText || 'Request failed';
}


/**
 * Sends an HTTP request to the specified API path, handling JSON bodies and error responses.
 * 
 * Single choke point for HTTP calls.
 *
 * AUTH: Right now, identity is the `X-User-Id` header (no real login). With OAuth2/OIDC this is where
 * the `Authorization: Bearer <access token>` header is attached and 401s trigger a silent
 * refresh or re-login. Keep tokens in memory (or use a backend-for-frontend with an httpOnly
 * cookie, this is my preference), never localStorage (XSS attack).
 * See backend/app/core/security.py for the full design.
 *
 * @export
 * @async
 * @template T 
 * @param {string} path 
 * @param {RequestInit} [init={}] 
 * @param {?number} [userId] 
 * @returns {Promise<T>} 
 */
export async function request<T>(
  path: string,
  init: RequestInit = {},
  userId?: number,
): Promise<T> {

  // Prepare headers for the request.
  const headers = new Headers(init.headers);
  if (init.body) headers.set('Content-Type', 'application/json');
  if (userId !== undefined) headers.set('X-User-Id', String(userId));

  // Determine the HTTP method for logging purposes.
  const method = init.method ?? 'GET';

  // Send the HTTP request and handle the response.
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  
  // Log and throw an error if the response is not OK.
  if (!response.ok) {
    const detail = await readDetail(response);
    logger.warn(`${method} ${path} -> ${response.status} ${detail}`);
    throw new ApiError(response.status, detail);
  }

  // At this point, the response is OK and can be processed.
  logger.info(`${method} ${path} -> ${response.status}`);
  return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
}
