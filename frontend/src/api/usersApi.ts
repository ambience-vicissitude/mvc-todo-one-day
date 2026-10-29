/**
 * API client for managing users.
 */
import type { User } from '../models/user';
import { request } from './client';

/**
 * API client for performing 'CR' only part of CRUD operations on users.
 * 
 * TRIM: No 'UD' to save some time.
 *
 * @type {{
 *  list: () => any;
 *  create: (name: string) => any;
 * }}
 */
export const usersApi = {
  list: () => request<User[]>('/users'),
  create: (name: string) =>
    request<User>('/users', { method: 'POST', body: JSON.stringify({ name }) }),
};
