/**
 * useAuth — Authentication state management hook.
 *
 * Features:
 * - Persistent login state via localStorage
 * - Automatic token hydration on mount
 * - Login / register / logout flows
 * - User info derived from token
 * - Loading state during auth operations
 */

"use client";

import { useCallback, useEffect, useState } from "react";
import {
  auth as authAPI,
  setAccessToken,
  type AuthResponse,
} from "../lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface User {
  userId: string;
  email: string;
  roles: string[];
}

export interface UseAuthResult {
  /** Current user or null if not authenticated */
  user: User | null;
  /** Whether the user is authenticated */
  isAuthenticated: boolean;
  /** Whether an auth operation is in progress */
  isLoading: boolean;
  /** Last auth error message */
  error: string | null;
  /** Login with email and password */
  login: (email: string, password: string) => Promise<boolean>;
  /** Register a new account */
  register: (email: string, password: string, fullName: string) => Promise<boolean>;
  /** Logout and clear token */
  logout: () => Promise<void>;
  /** Clear the error state */
  clearError: () => void;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const USER_STORAGE_KEY = "engineeros_user";

function persistUser(user: User | null): void {
  if (typeof window === "undefined") return;
  if (user) {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
  } else {
    localStorage.removeItem(USER_STORAGE_KEY);
  }
}

function authResponseToUser(response: AuthResponse): User {
  return {
    userId: response.user_id,
    email: response.email,
    roles: response.roles,
  };
}

// ---------------------------------------------------------------------------
// Global Auth Store (Zustand-style reactive vanilla state)
// ---------------------------------------------------------------------------

let globalUser: User | null = null;
let globalIsLoading = true;
let globalError: string | null = null;
const listeners = new Set<() => void>();
let isHydrated = false;

function updateGlobalState(user: User | null, isLoading: boolean, error: string | null) {
  globalUser = user;
  globalIsLoading = isLoading;
  globalError = error;
  listeners.forEach((listener) => listener());
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useAuth(): UseAuthResult {
  const [user, setUser] = useState<User | null>(globalUser);
  const [isLoading, setIsLoading] = useState(globalIsLoading);
  const [error, setError] = useState<string | null>(globalError);

  useEffect(() => {
    // Perform hydration on client side on first hook mount
    if (typeof window !== "undefined" && !isHydrated) {
      isHydrated = true;
      try {
        const token = localStorage.getItem("engineeros_token");
        const stored = localStorage.getItem(USER_STORAGE_KEY);
        if (token && stored) {
          globalUser = JSON.parse(stored) as User;
        } else {
          localStorage.removeItem("engineeros_token");
          localStorage.removeItem(USER_STORAGE_KEY);
          globalUser = null;
        }
      } catch {
        globalUser = null;
      }
      globalIsLoading = false;
      updateGlobalState(globalUser, false, null);
    }

    const handleChange = () => {
      setUser(globalUser);
      setIsLoading(globalIsLoading);
      setError(globalError);
    };

    listeners.add(handleChange);
    // Sync state immediately on mount
    handleChange();

    return () => {
      listeners.delete(handleChange);
    };
  }, []);

  const login = useCallback(async (email: string, password: string): Promise<boolean> => {
    updateGlobalState(globalUser, true, null);
    try {
      const response = await authAPI.login({ email, password });
      const newUser = authResponseToUser(response);
      persistUser(newUser);
      updateGlobalState(newUser, false, null);
      return true;
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Login failed. Please try again.";
      updateGlobalState(null, false, message);
      return false;
    }
  }, []);

  const register = useCallback(
    async (email: string, password: string, fullName: string): Promise<boolean> => {
      updateGlobalState(globalUser, true, null);
      try {
        const response = await authAPI.register({ email, password, full_name: fullName });
        const newUser = authResponseToUser(response);
        persistUser(newUser);
        updateGlobalState(newUser, false, null);
        return true;
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Registration failed. Please try again.";
        updateGlobalState(null, false, message);
        return false;
      }
    },
    []
  );

  const logout = useCallback(async (): Promise<void> => {
    updateGlobalState(globalUser, true, null);
    try {
      await authAPI.logout();
    } catch {
      // Ignore
    } finally {
      persistUser(null);
      setAccessToken(null);
      updateGlobalState(null, false, null);
    }
  }, []);

  const clearError = useCallback(() => {
    updateGlobalState(globalUser, globalIsLoading, null);
  }, []);

  return {
    user,
    isAuthenticated: user !== null,
    isLoading,
    error,
    login,
    register,
    logout,
    clearError,
  };
}
