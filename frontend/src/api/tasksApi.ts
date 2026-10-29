/**
 * API client for managing tasks.
 */

import type { Task, TaskChanges, TaskInput, TaskStatus } from '../models/task';
import { request } from './client';


/**
 * API client for performing CRUD operations on tasks.
 *
 * @type {{
 *  list: (userId: number, status?: TaskStatus) => any; 
 *  create: (userId: number, input: TaskInput) => any; 
 *  update: (userId: number, id: number, changes: TaskChanges) => any;
 *  remove: (userId: number, id: number) => any;
 * }}
 */
export const tasksApi = {
  list: (userId: number, status?: TaskStatus) =>
    request<Task[]>(`/tasks${status ? `?status=${status}` : ''}`, {}, userId),
  create: (userId: number, input: TaskInput) =>
    request<Task>('/tasks', { method: 'POST', body: JSON.stringify(input) }, userId),
  update: (userId: number, id: number, changes: TaskChanges) =>
    request<Task>(`/tasks/${id}`, { method: 'PATCH', body: JSON.stringify(changes) }, userId),
  remove: (userId: number, id: number) =>
    request<void>(`/tasks/${id}`, { method: 'DELETE' }, userId),
};
