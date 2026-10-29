/**
 * Component for creating a new task.
 */

import { useState, type FormEvent } from 'react';
import { TASK_STATUSES, type TaskInput, type TaskStatus } from '../models/task';


/**
 * Props for the TaskForm component.
 *
 * @interface Props
 * @typedef {Props}
 * 
 * @property {function} onSubmit - Function to handle form submission with the task input.
 */
interface Props {
  onSubmit: (input: TaskInput) => Promise<boolean>;
}


/**
 * Provides a form for creating a new task with title, description, status, and due date.
 *
 * @export
 * @param {Props} param0 
 * @param {(input: TaskInput) => Promise<boolean>} param0.onSubmit 
 * @returns {*} 
 */
export function TaskForm({ onSubmit }: Props) {

  // The useState hooks create the local state for the form fields.
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<TaskStatus>('todo');
  const [dueDate, setDueDate] = useState('');

  // The submit function handles form submission, validates input, and resets the form fields.
  const submit = async (event: FormEvent) => {
    event.preventDefault();

    if (!title.trim()) return;
    
    const succeeded = await onSubmit({ title: title.trim(), description, status, due_date: dueDate || null });
    // Do not reset the form if the submit was not success
    if (!succeeded) return;
    
    setTitle('');
    setDescription('');
    setStatus('todo');
    setDueDate('');
  };

  return (
    <form className="task-form" onSubmit={submit}>
      <input
        aria-label="Title"
        placeholder="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <textarea
        aria-label="Description"
        placeholder="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      <select
        aria-label="Status"
        value={status}
        onChange={(e) => setStatus(e.target.value as TaskStatus)}
      >
        {TASK_STATUSES.map((value) => (
          <option key={value} value={value}>
            {value}
          </option>
        ))}
      </select>
      <input
        type="date"
        aria-label="Due date"
        value={dueDate}
        onChange={(e) => setDueDate(e.target.value)}
      />
      <button type="submit">Add task</button>
    </form>
  );
}
