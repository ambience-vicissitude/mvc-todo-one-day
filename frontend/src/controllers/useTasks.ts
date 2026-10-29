
/**
 * Controller for the task list: owns state and orchestrates the API.
 *
 * Design notes:
 * - This hook holds state, which blurs the model/controller line. Classic MVC has no equivalent
 *   of hooks, so this is MVC-by-analogy (not true MVC: there is no observer pattern; React
 *   re-renders on state change instead).
 * - TRIMMED: manual fetching with a reload counter. In a real app, TanStack Query would replace
 *   most of this file (caching, refetching, optimistic updates, request de-duplication).
 */

import { useCallback, useEffect, useState } from 'react';
import { errorMessage } from '../api/client';
import { tasksApi } from '../api/tasksApi';
import type { Task, TaskChanges, TaskInput, TaskStatus } from '../models/task';


/**
 * Hook for managing tasks for a specific user.
 * Handles loading, error, fetching, filtering, and mutating tasks via the API.
 *
 * @export
 * @param {(number | null)} userId 
 * @returns {{
 *  tasks: any;
 *  filter: any;
 *  setFilter: any;
 *  loading: any;
 *  error: any;
 *  addTask: (input: TaskInput) => any;
 *  updateTask: (id: number, changes: Partial<TaskInput>) => any;
 *  removeTask: (id: number) => any;
 * }} 
 */
export function useTasks(userId: number | null) {

  // The useState hooks create the local state for Tasks
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filter, setFilter] = useState<TaskStatus | undefined>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  // The useEffect hook loads tasks whenever the userId, filter, or reloadKey changes.
  useEffect(() => {
    if (userId === null) {
      setTasks([]);
      return;
    }
    let cancelled = false; // ignore responses that arrive after the user/filter changed
    setLoading(true);
    tasksApi
      .list(userId, filter) // this triggers a fetch of tasks for the current user and filter
      .then((loaded) => {
        if (!cancelled) {
          setTasks(loaded);
          setError(null);
        }
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(errorMessage(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [userId, filter, reloadKey]); // NOTE: if any of these change, the tasks will be reloaded from the API

  // The mutate function wraps API actions and triggers a reload of tasks on success.
  const mutate = useCallback(async (action: () => Promise<unknown>) => {
    try {
      await action();
      setError(null);
      setReloadKey((key) => key + 1);
      return true;
    } catch (error: unknown) {
      setError(errorMessage(error));
      // Return false to indicate the action failed.
      return false;
    }
  }, []);

  // The addTask, updateTask, and removeTask functions use the mutate wrapper to perform API actions and reload tasks on success.
  // Note: these will be called by the UI components to perform task operations for the current user.
  const addTask = (input: TaskInput): Promise<boolean> =>
    userId === null ? Promise.resolve(false) : mutate(() => tasksApi.create(userId, input));
  const updateTask = (id: number, changes: TaskChanges) =>
    userId === null ? Promise.resolve() : mutate(() => tasksApi.update(userId, id, changes));
  const removeTask = (id: number) =>
    userId === null ? Promise.resolve() : mutate(() => tasksApi.remove(userId, id));

  // Return the state and action functions for use by UI components.
  return { tasks, filter, setFilter, loading, error, addTask, updateTask, removeTask };
}
