/**
 * Component for filtering tasks by status.
 */

import { TASK_STATUSES, type TaskStatus } from '../models/task';

/**
 * Props for the StatusFilter component.
 *
 * @interface Props
 * @typedef {Props}
 * 
 * @property {TaskStatus | undefined} value - The currently selected status.
 * @property {function} onChange - Function to handle status changes.
 */
interface Props {
  value: TaskStatus | undefined;
  onChange: (status: TaskStatus | undefined) => void;
}


/**
 * Provides a dropdown to select a specific status or view all tasks.
 *
 * @export
 * @param {Props} param0 
 * @param {*} param0.value 
 * @param {(status: any) => void} param0.onChange 
 * @returns {*} 
 */
export function StatusFilter({ value, onChange }: Props) {
  return (
    <label>
      Filter{' '}
      <select
        value={value ?? ''}
        onChange={(e) => onChange((e.target.value || undefined) as TaskStatus | undefined)}
      >
        <option value="">All</option>
        {TASK_STATUSES.map((status) => (
          <option key={status} value={status}>
            {status}
          </option>
        ))}
      </select>
    </label>
  );
}
