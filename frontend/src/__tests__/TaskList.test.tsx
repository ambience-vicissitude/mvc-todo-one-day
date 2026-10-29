/**
 * Tests for the TaskList component.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import type { Task } from '../models/task';
import { TaskList } from '../views/TaskList';

// TRIMMED: only the presentational view is tested; hooks and API client are covered by the
// compose integration test.

/**
 * A sample task used for testing the TaskList component.
 *
 * @type {Task}
 */
const task: Task = {
  id: 1,
  title: 'Write README',
  description: 'Explain the design',
  status: 'todo',
  due_date: null,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('TaskList', () => {
  it('shows an empty state', () => {
    render(<TaskList tasks={[]} onStatusChange={vi.fn()} onDelete={vi.fn()} />);
    expect(screen.getByText('No tasks yet.')).toBeInTheDocument();
  });

  it('reports status changes and deletions', async () => {
    const onStatusChange = vi.fn();
    const onDelete = vi.fn();
    render(<TaskList tasks={[task]} onStatusChange={onStatusChange} onDelete={onDelete} />);

    await userEvent.selectOptions(screen.getByLabelText('Status of Write README'), 'done');
    expect(onStatusChange).toHaveBeenCalledWith(1, 'done');

    await userEvent.click(screen.getByRole('button', { name: 'Delete Write README' }));
    expect(onDelete).toHaveBeenCalledWith(1);
  });
});
