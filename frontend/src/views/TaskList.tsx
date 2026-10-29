/**
 * Component for displaying a list of tasks with status and delete controls.
 */

import { TASK_STATUSES, type Task, type TaskStatus } from '../models/task';


/**
 * Props for the TaskList component.
 *
 * @interface Props
 * @typedef {Props}
 * 
 * @property {Task[]} tasks - The list of tasks to display.
 * @property {function} onStatusChange - Function to handle status changes for a task.
 * @property {function} onDelete - Function to handle deletion of a task.
 * 
 */
interface Props {
  tasks: Task[];
  onStatusChange: (id: number, status: TaskStatus) => void;
  onDelete: (id: number) => void;
}


/**
 * Displays a list of tasks with controls to change their status or delete them.
 *
 * @export
 * @param {Props} param0 
 * @param {{}} param0.tasks 
 * @param {(id: number, status: any) => void} param0.onStatusChange 
 * @param {(id: number) => void} param0.onDelete 
 * @returns {*} 
 */
export function TaskList({ tasks, onStatusChange, onDelete }: Props) {

  // If there are no tasks, display a message. TRIM: This can be a reusable component on its own.
  if (tasks.length === 0) return <p>No tasks yet.</p>;

  return (
    <ul className="task-list">
      {tasks.map((task) => (
        <li key={task.id}>
          <strong>{task.title}</strong>
          {task.description && <p>{task.description}</p>}
          {task.due_date && <small>Due {task.due_date}</small>}
          <select
            aria-label={`Status of ${task.title}`}
            value={task.status}
            onChange={(e) => onStatusChange(task.id, e.target.value as TaskStatus)}
          >
            {TASK_STATUSES.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
          <button aria-label={`Delete ${task.title}`} onClick={() => onDelete(task.id)}>
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}
