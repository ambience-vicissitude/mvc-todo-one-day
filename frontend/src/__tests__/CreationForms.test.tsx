import { act, cleanup, fireEvent, render, renderHook, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from '../App';
import { tasksApi } from '../api/tasksApi';
import { usersApi } from '../api/usersApi';
import { useTasks } from '../controllers/useTasks';
import type { Task } from '../models/task';

vi.mock('../api/tasksApi', () => ({
  tasksApi: { list: vi.fn(), create: vi.fn(), update: vi.fn(), remove: vi.fn() },
}));

vi.mock('../api/usersApi', () => ({
  usersApi: { list: vi.fn(), create: vi.fn() },
}));

const existingUser = { id: 1, name: 'Existing user', created_at: '2026-01-01T00:00:00Z' };
const createdTask: Task = {
  id: 1,
  title: 'Keep my draft',
  description: 'Detailed notes',
  status: 'doing',
  due_date: '2099-12-31',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

beforeEach(() => {
  vi.resetAllMocks();
  localStorage.clear();
  vi.mocked(usersApi.list).mockResolvedValue([existingUser]);
  vi.mocked(tasksApi.list).mockResolvedValue([]);
});

afterEach(() => {
  cleanup();
  localStorage.clear();
});

describe('Creation forms', () => {
  it('preserves every task field on failure and resets them after a successful retry', async () => {
    const user = userEvent.setup();
    localStorage.setItem('selectedUserId', String(existingUser.id));
    vi.mocked(tasksApi.create)
      .mockRejectedValueOnce(new Error('Task creation failed'))
      .mockResolvedValueOnce(createdTask);
    render(<App />);

    const title = await screen.findByLabelText('Title');
    await screen.findByText('No tasks yet.');
    const description = screen.getByLabelText('Description');
    const status = screen.getByLabelText('Status');
    const dueDate = screen.getByLabelText('Due date');
    await user.type(title, '  Keep my draft  ');
    await user.type(description, createdTask.description);
    await user.selectOptions(status, 'doing');
    fireEvent.change(dueDate, { target: { value: createdTask.due_date } });
    await user.click(screen.getByRole('button', { name: 'Add task' }));

    expect(await screen.findByRole('alert')).toHaveTextContent('Task creation failed');
    expect(title).toHaveValue('  Keep my draft  ');
    expect(description).toHaveValue(createdTask.description);
    expect(status).toHaveValue('doing');
    expect(dueDate).toHaveValue(createdTask.due_date);
    expect(tasksApi.list).toHaveBeenCalledTimes(1);
    expect(tasksApi.create).toHaveBeenLastCalledWith(existingUser.id, {
      title: createdTask.title,
      description: createdTask.description,
      status: createdTask.status,
      due_date: createdTask.due_date,
    });

    vi.mocked(tasksApi.list).mockResolvedValue([createdTask]);
    await user.click(screen.getByRole('button', { name: 'Add task' }));

    expect(await screen.findByText(createdTask.title)).toBeInTheDocument();
    await waitFor(() => expect(title).toHaveValue(''));
    expect(description).toHaveValue('');
    expect(status).toHaveValue('todo');
    expect(dueDate).toHaveValue('');
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(tasksApi.create).toHaveBeenCalledTimes(2);
    expect(tasksApi.list).toHaveBeenCalledTimes(2);
  });

  it('preserves the user name and selection on failure and selects the user after retry', async () => {
    const user = userEvent.setup();
    const createdUser = { ...existingUser, id: 2, name: 'New user' };
    localStorage.setItem('selectedUserId', String(existingUser.id));
    vi.mocked(usersApi.create)
      .mockRejectedValueOnce(new Error('User creation failed'))
      .mockResolvedValueOnce(createdUser);
    render(<App />);

    await screen.findByText('No tasks yet.');
    const name = screen.getByLabelText('New user name');
    await user.type(name, '  New user  ');
    await user.click(screen.getByRole('button', { name: 'Add user' }));

    expect(await screen.findByRole('alert')).toHaveTextContent('User creation failed');
    expect(name).toHaveValue('  New user  ');
    expect(screen.getByLabelText('User')).toHaveValue(String(existingUser.id));
    expect(localStorage.getItem('selectedUserId')).toBe(String(existingUser.id));
    expect(screen.queryByRole('option', { name: 'New user' })).not.toBeInTheDocument();
    expect(usersApi.create).toHaveBeenLastCalledWith('New user');

    await user.click(screen.getByRole('button', { name: 'Add user' }));

    expect(await screen.findByRole('option', { name: 'New user' })).toBeInTheDocument();
    await waitFor(() => expect(name).toHaveValue(''));
    expect(screen.getByLabelText('User')).toHaveValue(String(createdUser.id));
    expect(localStorage.getItem('selectedUserId')).toBe(String(createdUser.id));
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(usersApi.create).toHaveBeenCalledTimes(2);
  });

  it('ignores whitespace-only names and titles without clearing them', async () => {
    const user = userEvent.setup();
    localStorage.setItem('selectedUserId', String(existingUser.id));
    render(<App />);

    const title = await screen.findByLabelText('Title');
    const name = screen.getByLabelText('New user name');
    await user.type(name, '   ');
    await user.type(title, '   ');
    await user.click(screen.getByRole('button', { name: 'Add user' }));
    await user.click(screen.getByRole('button', { name: 'Add task' }));

    expect(usersApi.create).not.toHaveBeenCalled();
    expect(tasksApi.create).not.toHaveBeenCalled();
    expect(name).toHaveValue('   ');
    expect(title).toHaveValue('   ');
  });

  it('returns false without calling the API when task creation has no selected user', async () => {
    const { result } = renderHook(() => useTasks(null));

    await act(async () => {
      expect(await result.current.addTask({ title: 'No user' })).toBe(false);
    });

    expect(tasksApi.create).not.toHaveBeenCalled();
    expect(tasksApi.list).not.toHaveBeenCalled();
  });
});