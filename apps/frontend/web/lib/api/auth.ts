
// frontend/web/lib/api/auth.ts

import { apiClient } from "./client";

/* -------------------------------------------------------------------------- */
/* Types                                                                      */
/* -------------------------------------------------------------------------- */

export interface RegisterRequest {
  email: string;
  password: string;
  username?: string | null;
  full_name?: string | null;
  accept_terms: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirmRequest {
  token: string;
  new_password: string;
}

export interface EmailVerificationRequest {
  token: string;
}

export type UserRole =
  | "user"
  | "admin"
  | "moderator"
  | "premium";

export type AccountStatus =
  | "active"
  | "inactive"
  | "suspended"
  | "pending_verification";

export interface UserResponse {
  id: number;
  email: string;
  username?: string | null;
  full_name?: string | null;
  role?: UserRole;
  account_status?: AccountStatus;
  is_verified?: boolean;
  created_at: string;
  last_login?: string | null;
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string | null;
  token_type: string;
  expires_in: number;
  user: UserResponse;
}

export interface AuthErrorResponse {
  error: string;
  message: string;
  details?: Record<string, unknown> | null;
}

/* -------------------------------------------------------------------------- */
/* Token Storage                                                              */
/*                                                                            */
/* Delegates to the shared `tokenStorage` singleton. Previously this module    */
/* used its own localStorage keys ("access_token" / "refresh_token") while     */
/* lib/api/client.ts read "auth_token" — two disconnected stores. Since the    */
/* live auth path is features/auth/provider.tsx -> tokenStorage, this module   */
/* is currently unreferenced, but the divergence was a latent bug for any      */
/* future caller. Both now share one source of truth.                          */
/* -------------------------------------------------------------------------- */

import { tokenStorage } from "@/services/storage/token";

function storeTokens(response: TokenResponse): void {
  tokenStorage.setTokens(
    response.access_token,
    response.refresh_token ?? "",
    response.expires_in
  );
}

function clearTokens(): void {
  tokenStorage.clear();
}

export function getAccessToken(): string | null {
  return tokenStorage.getAccessToken();
}

export function getRefreshToken(): string | null {
  return tokenStorage.getRefreshToken();
}

export function isAuthenticated(): boolean {
  return tokenStorage.getAccessToken() !== null;
}

/* -------------------------------------------------------------------------- */
/* Authentication API                                                         */
/* -------------------------------------------------------------------------- */

/**
 * Register a new user.
 */
export async function register(
  data: RegisterRequest
): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>(
    "/auth/register",
    data
  );

  storeTokens(response);

  return response;
}

/**
 * Login an existing user.
 */
export async function login(
  data: LoginRequest
): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>(
    "/auth/login",
    data
  );

  storeTokens(response);

  return response;
}

/**
 * Refresh the access token.
 */
export async function refreshToken(
  refreshTokenValue?: string
): Promise<TokenResponse> {
  const token =
    refreshTokenValue ?? getRefreshToken();

  if (!token) {
    throw new Error("No refresh token available.");
  }

  const response =
    await apiClient.post<TokenResponse>(
      "/auth/refresh",
      {
        refresh_token: token,
      }
    );

  storeTokens(response);

  return response;
}

/**
 * Logout the current user.
 */
export async function logout(): Promise<void> {
  try {
    await apiClient.post<void>("/auth/logout");
  } finally {
    clearTokens();
  }
}

/**
 * Get the currently authenticated user.
 */
export async function getCurrentUser(): Promise<UserResponse> {
  return apiClient.get<UserResponse>("/auth/me");
}

/* -------------------------------------------------------------------------- */
/* Password Reset                                                             */
/* -------------------------------------------------------------------------- */

/**
 * Request a password reset email.
 */
export async function requestPasswordReset(
  data: PasswordResetRequest
): Promise<Record<string, string>> {
  return apiClient.post<Record<string, string>>(
    "/auth/password-reset",
    data
  );
}

/**
 * Confirm a password reset using the reset token.
 */
export async function confirmPasswordReset(
  data: PasswordResetConfirmRequest
): Promise<Record<string, string>> {
  return apiClient.post<Record<string, string>>(
    "/auth/password-reset/confirm",
    data
  );
}

/* -------------------------------------------------------------------------- */
/* Email Verification                                                         */
/* -------------------------------------------------------------------------- */

/**
 * Verify a user's email address.
 */
export async function verifyEmail(
  data: EmailVerificationRequest
): Promise<Record<string, string>> {
  return apiClient.post<Record<string, string>>(
    "/auth/verify-email",
    data
  );
}

/**
 * Resend the verification email.
 */
export async function resendVerification(
  email: string
): Promise<Record<string, string>> {
  const query = new URLSearchParams({
    email,
  });

  return apiClient.post<Record<string, string>>(
    `/auth/resend-verification?${query.toString()}`
  );
}

/* -------------------------------------------------------------------------- */
/* Helpers                                                                    */
/* -------------------------------------------------------------------------- */

/**
 * Clear locally stored authentication credentials.
 */
export function clearAuthentication(): void {
  clearTokens();
}
