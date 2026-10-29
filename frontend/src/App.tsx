/**
 * Main application component for managing tasks and users.
 */

import { useTasks } from './controllers/useTasks';
import { useUsers } from './controllers/useUsers';
import { StatusFilter } from './views/StatusFilter';
import { TaskForm } from './views/TaskForm';
import { TaskList } from './views/TaskList';
import { UserPicker } from './views/UserPicker';

/**
 * @returns JSX.Element representing the main application component.
 */
export function App() {
  const { users, selectedUserId, selectUser, addUser, error: userError } = useUsers();
  const { tasks, filter, setFilter, loading, error, addTask, updateTask, removeTask } =
    useTasks(selectedUserId);

  return (
    <main>
      <h1>Task Manager</h1>
      <UserPicker
        users={users}
        selectedUserId={selectedUserId}
        onSelect={selectUser}
        onAdd={addUser}
      />
      {(userError || error) && <p role="alert">{userError ?? error}</p>}

      {selectedUserId === null ? (
        <p>Select or create a user to manage tasks.</p>
      ) : (
        <>
          <TaskForm onSubmit={addTask} />
          <StatusFilter value={filter} onChange={setFilter} />
          {loading ? (
            <p>Loading...</p>
          ) : (
            <TaskList
              tasks={tasks}
              onStatusChange={(id, status) => updateTask(id, { status })}
              onDelete={removeTask}
            />
          )}
        </>
      )}
    </main>
  );
}
