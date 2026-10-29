/**
 * Task model definitions for the application.
 */

/**
 * Task statuses used in the application.
 *
 * @type {readonly ["todo", "doing", "done"]}
 */
export const TASK_STATUSES = ['todo', 'doing', 'done'] as const;
export type TaskStatus = (typeof TASK_STATUSES)[number];


/**
 * Task entity representing a single task in the application.
 *
 * @export
 * @interface Task
 * @typedef {Task}
 */
export interface Task {
  id: number;
  title: string;
  description: string;
  status: TaskStatus;
  due_date: string | null;
  created_at: string;
  updated_at: string;
}


/**
 * Task input data used for creating or updating a task.
 *
 * @export
 * @interface TaskInput
 * @typedef {TaskInput}
 */
export interface TaskInput {
  title: string;
  description?: string;
  status?: TaskStatus;
  due_date?: string | null;
}

export type TaskChanges = Partial<TaskInput>;
