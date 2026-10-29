/**
 * Component for selecting a user and adding new users.
 */

import { useState, type FormEvent } from 'react';
import type { User } from '../models/user';


/**
 * Props for the UserPicker component.
 *
 * @interface Props
 * @typedef {Props}
 * 
 * @property {User[]} users - The list of available users.
 * @property {number | null} selectedUserId - The ID of the currently selected user.
 * @property {function} onSelect - Function to handle user selection changes.
 * @property {function} onAdd - Function to handle adding a new user.
 */
interface Props {
  users: User[];
  selectedUserId: number | null;
  onSelect: (id: number | null) => void;
  onAdd: (name: string) => Promise<void>;
}


/**
 * Component for selecting a user and adding new users.
 *
 * @export
 * @param {Props} param0 
 * @param {{}} param0.users 
 * @param {number} param0.selectedUserId 
 * @param {(id: number) => void} param0.onSelect 
 * @param {(name: string) => Promise<void>} param0.onAdd 
 * @returns {*} 
 */
export function UserPicker({ users, selectedUserId, onSelect, onAdd }: Props) {

  // State for the new user's name.
  const [name, setName] = useState('');

  // Handles the form submission for adding a new user.
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!name.trim()) return;
    await onAdd(name.trim()); // trim the name just in case of typos
    setName('');
  };

  return (
    <section className="user-picker">
      <label>
        User{' '}
        <select
          value={selectedUserId ?? ''}
          onChange={(e) => onSelect(e.target.value ? Number(e.target.value) : null)}
        >
          <option value="">Select a user</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>
              {user.name}
            </option>
          ))}
        </select>
      </label>
      <form onSubmit={submit}>
        <input
          aria-label="New user name"
          placeholder="New user name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <button type="submit">Add user</button>
      </form>
    </section>
  );
}
