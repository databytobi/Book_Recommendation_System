// apps/frontend/web/features/auth/useAuth.ts

/**
 * useAuth Hook
 * 
 * Custom hook for accessing authentication context.
 */

"use client";

import { useContext } from "react";
import { AuthContext } from "./context";
import type { AuthContextType } from "./types";

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}

// ============================================================
// Convenience Hooks
// ============================================================

export function useUser() {
  const { user } = useAuth();
  return user;
}

export function useIsAuthenticated() {
  const { isAuthenticated } = useAuth();
  return isAuthenticated;
}

export function useIsAdmin() {
  const { isAdmin } = useAuth();
  return isAdmin();
}

export function useHasRole(role: string) {
  const { hasRole } = useAuth();
  return hasRole(role);
}

export function useAuthLoading() {
  const { loading } = useAuth();
  return loading;
}

export function useAuthError() {
  const { error } = useAuth();
  return error;
}

export default useAuth;