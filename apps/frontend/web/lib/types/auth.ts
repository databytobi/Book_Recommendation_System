/**
 * ================================================================
 * 🔐 Auth Types
 * ================================================================
 *
 * These types define the authentication system's data structures.
 * They handle:
 * - User authentication
 * - Login/Register requests and responses
 * - Session management
 * - Password reset
 * ================================================================
 */

import type { ID, Timestamp } from "./common";
import type { User, UserPreferences } from "./user";

// ============================================================
// 👤 User Types (re-exported from user.ts)
// ============================================================

export type { User, UserPreferences };

// ============================================================
// 🔐 Auth Types
// ============================================================

export interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface LoginResponse {
  user: User;
  token: string;
  refreshToken?: string;
  expiresIn: number; // seconds
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  firstName?: string;
  lastName?: string;
}

export interface RegisterResponse {
  user: User;
  token: string;
  message: string;
}

export interface RefreshTokenRequest {
  refreshToken: string;
}

export interface RefreshTokenResponse {
  token: string;
  expiresIn: number;
}

export interface LogoutResponse {
  success: boolean;
  message: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetResponse {
  success: boolean;
  message: string;
  resetToken?: string;
}

export interface PasswordUpdateRequest {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface VerifyEmailRequest {
  token: string;
}

export interface VerifyEmailResponse {
  success: boolean;
  message: string;
}

// ============================================================
// 🍪 Session Types
// ============================================================

export interface Session {
  user: User;
  token: string;
  expiresAt: Timestamp;
  isAuthenticated: boolean;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// ============================================================
// 🏗️ Factory Functions
// ============================================================

export function createEmptyUser(): User {
  return {
    id: "",
    username: "",
    email: "",
    fullName: "",
    role: "user",
    isVerified: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
}

export function createEmptyAuthState(): AuthState {
  return {
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
  };
}

export function createSession(user: User, token: string, expiresIn: number): Session {
  return {
    user,
    token,
    expiresAt: new Date(Date.now() + expiresIn * 1000).toISOString(),
    isAuthenticated: true,
  };
}