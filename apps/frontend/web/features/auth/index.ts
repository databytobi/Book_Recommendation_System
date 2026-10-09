// apps/frontend/web/features/auth/index.ts

/**
 * Auth Module Index
 * 
 * Central export point for all authentication-related features.
 */

// ============================================================
// Import everything we want to export
// ============================================================

// Components
import { AuthProvider as AuthProviderComponent } from "./provider";
import { 
  AuthContext as AuthContextObject,
  useAuth as useAuthHook,
  useUser as useUserHook,
  useIsAuthenticated as useIsAuthenticatedHook,
  useIsAdmin as useIsAdminHook,
  useHasRole as useHasRoleHook,
  useAuthLoading as useAuthLoadingHook,
  useAuthError as useAuthErrorHook,
  WithAuth as WithAuthComponent,
  GuestRoute as GuestRouteComponent,
} from "./context";

// Services
import { authService as authServiceInstance } from "./service";

// Types - Imported but not directly exported as a namespace
// FIX: Removed unused 'AuthTypes' import

// ============================================================
// Export everything individually
// ============================================================

// Components
export { AuthProviderComponent as AuthProvider };
export { default as AuthProviderDefault } from "./provider";

// Context & Hooks
export { 
  AuthContextObject as AuthContext,
  useAuthHook as useAuth,
  useUserHook as useUser,
  useIsAuthenticatedHook as useIsAuthenticated,
  useIsAdminHook as useIsAdmin,
  useHasRoleHook as useHasRole,
  useAuthLoadingHook as useAuthLoading,
  useAuthErrorHook as useAuthError,
  WithAuthComponent as WithAuth,
  GuestRouteComponent as GuestRoute,
};

export { default as AuthContextDefault } from "./context";

// Services
export { authServiceInstance as authService };
export { default as authServiceDefault } from "./service";

// Types
export type {
  LoginRequest,
  RegisterRequest,
  RefreshTokenRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  ChangePasswordRequest,
  VerifyEmailRequest,
  LoginResponse,
  RefreshTokenResponse,
  ApiResponse,
  User,
  AuthResponse,
  AuthError,
  ApiError,
  AuthContextType,
  AuthState,
  AuthActions,
  AuthStore,
  AuthTokens,
  AuthValidation,
} from "./types";

// Type Guards
export { isUser, isAuthError } from "./types";

// ============================================================
// Default Export
// ============================================================

const authModule = {
  // Components
  AuthProvider: AuthProviderComponent,
  WithAuth: WithAuthComponent,
  GuestRoute: GuestRouteComponent,
  
  // Context
  AuthContext: AuthContextObject,
  
  // Hooks
  useAuth: useAuthHook,
  useUser: useUserHook,
  useIsAuthenticated: useIsAuthenticatedHook,
  useIsAdmin: useIsAdminHook,
  useHasRole: useHasRoleHook,
  useAuthLoading: useAuthLoadingHook,
  useAuthError: useAuthErrorHook,
  
  // Services
  authService: authServiceInstance,
};

export default authModule;