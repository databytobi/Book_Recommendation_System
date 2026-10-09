// apps/frontend/web/features/auth/types.ts

/**
 * Auth Types
 * 
 * Type definitions for authentication-related data structures.
 */

// ============================================================
// Request Types
// ============================================================

export interface LoginRequest {
  email?: string;
  username?: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  confirm_password: string;
  username?: string;
  full_name?: string;
  accept_terms: boolean;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface VerifyEmailRequest {
  token: string;
}

// ============================================================
// Response Types
// ============================================================

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  is_active: boolean;
  is_verified: boolean;
  is_superuser?: boolean;
  roles?: string[];
  permissions?: string[];
  created_at: string;
  updated_at?: string;
}

export interface AuthResponse<T = unknown> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}

// ============================================================
// Error Types
// ============================================================

export interface AuthError {
  status: number;
  message: string;
  code?: string;
  detail?: string;
  field?: string;
}

export interface ApiError {
  status: number;
  message: string;
  code?: string;
  detail?: string;
}

// ============================================================
// Context Types
// ============================================================

export interface AuthContextType {
  // State
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  isInitialized: boolean;
  error: AuthError | null;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  updateUser: (user: User) => void;
  clearError: () => void;
  
  // Helpers
  hasRole: (role: string) => boolean;
  isAdmin: () => boolean;
}

// ============================================================
// State Types (for Zustand/Redux)
// ============================================================

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: AuthError | null;
  token: string | null;
}

export interface AuthActions {
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  getCurrentUser: () => Promise<void>;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  clearError: () => void;
}

export type AuthStore = AuthState & AuthActions;

// ============================================================
// Utility Types
// ============================================================

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthValidation {
  isValid: boolean;
  errors: Record<string, string>;
}

// ============================================================
// Type Guards
// ============================================================

export function isUser(obj: unknown): obj is User {
  return (
    obj !== null &&
    typeof obj === 'object' &&
    'id' in obj &&
    'username' in obj &&
    'email' in obj
  );
}

export function isAuthError(obj: unknown): obj is AuthError {
  return (
    obj !== null &&
    typeof obj === 'object' &&
    'status' in obj &&
    'message' in obj
  );
}

// ============================================================
// Export All Types
// ============================================================

export type {
  LoginRequest as LoginRequestType,
  RegisterRequest as RegisterRequestType,
  RefreshTokenRequest as RefreshTokenRequestType,
  ForgotPasswordRequest as ForgotPasswordRequestType,
  ResetPasswordRequest as ResetPasswordRequestType,
  ChangePasswordRequest as ChangePasswordRequestType,
  VerifyEmailRequest as VerifyEmailRequestType,
  LoginResponse as LoginResponseType,
  RefreshTokenResponse as RefreshTokenResponseType,
  ApiResponse as ApiResponseType,
  User as UserType,
  AuthResponse as AuthResponseType,
  AuthError as AuthErrorType,
  ApiError as ApiErrorType,
  AuthContextType as AuthContextTypeType,
  AuthState as AuthStateType,
  AuthActions as AuthActionsType,
  AuthStore as AuthStoreType,
  AuthTokens as AuthTokensType,
  AuthValidation as AuthValidationType,
};