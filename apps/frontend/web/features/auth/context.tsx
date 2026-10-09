"use client";

import {
  createContext,
  useContext,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";

import type { AuthContextType } from "./types";

export const AuthContext = createContext<AuthContextType | undefined>(
  undefined
);

// ============================================================
// Auth hook
// ============================================================

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}

// ============================================================
// Convenience hooks
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

// ============================================================
// Auth wrapper
// ============================================================

interface AuthWrapperProps {
  children: ReactNode;
  fallback?: ReactNode;
}

export function WithAuth({
  children,
  fallback = null,
}: AuthWrapperProps) {
  const { isAuthenticated, isInitialized } = useAuth();

  if (!isInitialized) {
    return fallback;
  }

  if (!isAuthenticated) {
    return fallback;
  }

  return <>{children}</>;
}

// ============================================================
// Guest-only wrapper
// ============================================================

interface GuestRouteProps {
  children: ReactNode;
  fallback?: ReactNode;
}

export function GuestRoute({
  children,
  fallback = null,
}: GuestRouteProps) {
  const router = useRouter();
  const { isAuthenticated, isInitialized } = useAuth();

  if (!isInitialized) {
    return fallback;
  }

  if (isAuthenticated) {
    router.replace("/dashboard");
    return fallback;
  }

  return <>{children}</>;
}

export default AuthContext;