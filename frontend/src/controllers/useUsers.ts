/**
 * Controller for the user picker: owns state and orchestrates the API.
 */

import { useEffect, useState } from 'react';
import { errorMessage } from '../api/client';
import { usersApi } from '../api/usersApi';
import type { User } from '../models/user';

// Not a credential: only remembers which user the picker had selected.
const STORAGE_KEY = 'selectedUserId';


/**
 * Hook for managing the user picker.
 * Handles loading users, selecting a user, and adding new users.
 * 
 * TRIM: Controller for the user picker (identity here is a plain selection; see core/security.py).
 * 
 * @export
 * @returns {{
 *  users: any;
 *  selectedUserId: any;
 *  selectUser: (id: number) => void;
 *  addUser: (name: string) => any;
 *  error: any;
 * }} 
 */
export function useUsers() {

  // The useState hooks create the local state for the user picker.
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  // The useEffect hook loads the list of users from the API when the component mounts.
  useEffect(() => {
    usersApi
      .list() // this triggers a fetch of all users from the API
      .then((loaded) => {
        setUsers(loaded);
        const stored = Number(localStorage.getItem(STORAGE_KEY));
        setSelectedUserId(loaded.some((user) => user.id === stored) ? stored : null);
      })
      .catch((e: unknown) => setError(errorMessage(e)));
  }, []);

  // The selectUser function updates the selected user and persists it to localStorage.
  // Note: This is fine since it does not store any sensitive credentials.
  const selectUser = (id: number | null) => {
    setSelectedUserId(id);
    if (id === null) localStorage.removeItem(STORAGE_KEY);
    else localStorage.setItem(STORAGE_KEY, String(id));
  };

  // The addUser function creates a new user via the API and selects it.
  const addUser = async (name: string): Promise<boolean> => {
    try {
      const user = await usersApi.create(name);
      setUsers((previous) => [...previous, user]);
      selectUser(user.id);
      setError(null);
      return true;
    } catch (e) {
      setError(errorMessage(e));
      // Return false to indicate the user was not added successfully.
      return false;
    }
  };

  // Return the state and action functions for use by UI components.
  return { users, selectedUserId, selectUser, addUser, error };
}
