/**
 * useAuth Hook
 * 
 * Custom hook for accessing authentication context.
 * Provides user data, authentication status, and auth actions.
 * 
 * @throws {Error} If used outside of AuthProvider
 * @returns {AuthContextType} Authentication context value
 */

"use client";

import { useContext, useMemo, useCallback } from "react";
import { AuthContext } from "./context";
import type { AuthContextType, User } from "./types";

// ============================================================
// Type Definitions
// ============================================================

interface UseAuthOptions {
  /**
   * Whether to throw an error if used outside AuthProvider
   * @default true
   */
  throwIfMissing?: boolean;

  /**
   * Whether to automatically check token expiration
   * @default false
   */
  checkExpiry?: boolean;
}

interface UseAuthReturn extends AuthContextType {
  /**
   * Alias for isAuthenticated
   */
  readonly loggedIn: boolean;

  /**
   * Check if the user has a specific permission
   */
  hasPermission: (permission: string) => boolean;

  /**
   * Check if the user has any of the given permissions
   */
  hasAnyPermission: (permissions: string[]) => boolean;

  /**
   * Check if the user has all of the given permissions
   */
  hasAllPermissions: (permissions: string[]) => boolean;

  /**
   * Get the user's full name or username
   */
  getDisplayName: () => string;

  /**
   * Get the user's avatar URL or fallback
   */
  getAvatar: (fallback?: string) => string;
}

// ============================================================
// Error Messages
// ============================================================

const ERROR_MESSAGES = {
  CONTEXT_MISSING: "useAuth must be used within an AuthProvider",
  CONTEXT_UNDEFINED: "Auth context is undefined",
} as const;

// ============================================================
// Main Hook
// ============================================================

export function useAuth(options: UseAuthOptions = {}): UseAuthReturn {
  const { 
    throwIfMissing = true, 
    checkExpiry = false 
  } = options;

  const context = useContext(AuthContext);

  // FIX 1: Remove early return - only throw if requested
  // Always use a valid object afterwards
  if (!context && throwIfMissing) {
    throw new Error(ERROR_MESSAGES.CONTEXT_MISSING);
  }

  // Always use a valid object afterwards
  const auth = context ?? createSafeFallback();

  // Check token expiration if requested
  if (checkExpiry && auth.user) {
    // This would typically check token expiration
    // You can add logic here to check if the token is expired
  }

  // ============================================================
  // Helper Functions
  // ============================================================

  /**
   * Check if the user has a specific permission
   */
  const hasPermission = useCallback((permission: string): boolean => {
    if (!auth.user) return false;
    
    // FIX 3: Remove any cast - use optional chaining
    const permissions = auth.user?.permissions ?? [];
    return permissions.includes(permission);
  }, [auth.user]);

  /**
   * Check if the user has any of the given permissions
   */
  const hasAnyPermission = useCallback((permissions: string[]): boolean => {
    if (!auth.user || !permissions.length) return false;
    return permissions.some((perm) => hasPermission(perm));
  }, [auth.user, hasPermission]);

  /**
   * Check if the user has all of the given permissions
   */
  const hasAllPermissions = useCallback((permissions: string[]): boolean => {
    if (!auth.user) return false;
    if (!permissions.length) return true;
    return permissions.every((perm) => hasPermission(perm));
  }, [auth.user, hasPermission]);

  /**
   * Get the user's display name
   */
  const getDisplayName = useCallback((): string => {
    if (!auth.user) return "Guest";
    return auth.user.full_name || auth.user.username || "User";
  }, [auth.user]);

  /**
   * Get the user's avatar URL
   */
  const getAvatar = useCallback((fallback?: string): string => {
    if (!auth.user) return fallback || "";
    return auth.user.avatar_url || fallback || "";
  }, [auth.user]);

  // ============================================================
  // Memoized Return Value
  // ============================================================

  // FIX 5: Update memo to use auth instead of context
  return useMemo(() => ({
    // Original auth values
    user: auth.user,
    loading: auth.loading,
    isAuthenticated: auth.isAuthenticated,
    isInitialized: auth.isInitialized,
    error: auth.error,
    login: auth.login,
    register: auth.register,
    logout: auth.logout,
    refreshUser: auth.refreshUser,
    updateUser: auth.updateUser,
    clearError: auth.clearError,
    hasRole: auth.hasRole,
    isAdmin: auth.isAdmin,

    // Additional helpers
    loggedIn: auth.isAuthenticated,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    getDisplayName,
    getAvatar,
  }), [
    // FIX 4: Update dependencies to use auth instead of context
    auth,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    getDisplayName,
    getAvatar,
  ]);
}

// ============================================================
// Fallback Functions
// ============================================================

/**
 * Create a safe fallback when useAuth is used outside AuthProvider
 * and throwIfMissing is false
 */
function createSafeFallback(): UseAuthReturn {
  const noop = async () => {};
  const voidFn = () => {};

  return {
    // State
    user: null,
    loading: false,
    isAuthenticated: false,
    isInitialized: false,
    error: null,

    // Actions (no-op)
    login: noop,
    register: noop,
    logout: noop,
    refreshUser: noop,
    updateUser: voidFn,
    clearError: voidFn,

    // Helpers
    hasRole: () => false,
    isAdmin: () => false,
    loggedIn: false,
    hasPermission: () => false,
    hasAnyPermission: () => false,
    hasAllPermissions: () => false,
    getDisplayName: () => "Guest",
    getAvatar: () => "",
  };
}

// ============================================================
// Convenience Hooks
// ============================================================

/**
 * Hook that only returns user data (optimized for performance)
 */
export function useUser(): User | null {
  const { user } = useAuth();
  return user;
}

/**
 * Hook that only returns authentication status
 */
export function useIsAuthenticated(): boolean {
  const { isAuthenticated } = useAuth();
  return isAuthenticated;
}

/**
 * Hook that returns user roles
 */
export function useUserRoles(): string[] {
  const { user } = useAuth();
  // FIX 6: Remove any cast - use optional chaining
  return user?.roles ?? [];
}

/**
 * Hook that checks if user has a specific role
 */
export function useHasRole(role: string): boolean {
  const { hasRole } = useAuth();
  return hasRole(role);
}

/**
 * Hook that checks if user is admin
 */
export function useIsAdmin(): boolean {
  const { isAdmin } = useAuth();
  return isAdmin();
}

// ============================================================
// Default Export
// ============================================================

export default useAuth;