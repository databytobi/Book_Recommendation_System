/**
 * Auth Service
 * 
 * Handles all authentication-related API calls including login,
 * registration, logout, and user management.
 */

import { apiClient } from "@/lib/api/client";

// FIX: Removed unused 'tokenStorage' import
import {
  LoginRequest,
  RegisterRequest,
  LoginResponse,
  User,
  RefreshTokenResponse,
  ApiResponse,
  AuthError,
} from "./types";

// ============================================================
// Auth Service Class
// ============================================================

class AuthService {
  /**
   * Authenticate a user with email/username and password
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    try {
      return await apiClient.post<LoginResponse>("/auth/login", data);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Register a new user
   */
  async register(data: RegisterRequest): Promise<User> {
    try {
      return await apiClient.post<User>("/auth/register", data);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Log out the current user
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post("/auth/logout");
    } catch (error) {
      console.error("Logout error:", error);
      throw this.handleError(error);
    }
  }

  /**
   * Get the current authenticated user's profile
   */
  async getCurrentUser(): Promise<User> {
    try {
      return await apiClient.get<User>("/auth/me");
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Refresh the access token using a refresh token
   */
  async refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
    try {
      return await apiClient.post<RefreshTokenResponse>("/auth/refresh", {
        refresh_token: refreshToken,
      });
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Request a password reset email
   */
  async forgotPassword(email: string): Promise<ApiResponse> {
    try {
      return await apiClient.post<ApiResponse>("/auth/forgot-password", {
        email,
      });
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Reset password using a token
   */
  async resetPassword(token: string, newPassword: string): Promise<ApiResponse> {
    try {
      return await apiClient.post<ApiResponse>("/auth/reset-password", {
        token,
        new_password: newPassword,
      });
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Verify email address
   */
  async verifyEmail(token: string): Promise<ApiResponse> {
    try {
      return await apiClient.post<ApiResponse>("/auth/verify-email", {
        token,
      });
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Change user password (requires authentication)
   */
  async changePassword(
    currentPassword: string,
    newPassword: string
  ): Promise<ApiResponse> {
    try {
      return await apiClient.post<ApiResponse>("/auth/change-password", {
        current_password: currentPassword,
        new_password: newPassword,
      });
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Update user profile
   */
  async updateProfile(data: Partial<User>): Promise<User> {
    try {
      return await apiClient.put<User>("/auth/profile", data);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Handle API errors consistently
   */
  private handleError(error: unknown): AuthError {
    // If it's already an AuthError, return it
    if (error && typeof error === 'object' && 'status' in error) {
      return error as AuthError;
    }

    // If it's an axios error
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { 
        response?: { 
          status?: number; 
          data?: { detail?: string; message?: string; error?: string } 
        } 
      };
      const status = axiosError.response?.status || 500;
      const message = axiosError.response?.data?.detail || 
                     axiosError.response?.data?.message ||
                     axiosError.response?.data?.error ||
                     "An unexpected error occurred";

      return {
        status,
        message,
        code: status.toString(),
      };
    }

    // Unknown error
    return {
      status: 500,
      message: error instanceof Error ? error.message : "An unexpected error occurred",
      code: "500",
    };
  }
}

// ============================================================
// Export Singleton Instance
// ============================================================

export const authService = new AuthService();

// ============================================================
// Export Individual Functions (for easier imports)
// ============================================================

export const login = (data: LoginRequest) => authService.login(data);
export const register = (data: RegisterRequest) => authService.register(data);
export const logout = () => authService.logout();
export const getCurrentUser = () => authService.getCurrentUser();
export const refreshToken = (token: string) => authService.refreshToken(token);
export const forgotPassword = (email: string) => authService.forgotPassword(email);
export const resetPassword = (token: string, newPassword: string) => 
  authService.resetPassword(token, newPassword);
export const verifyEmail = (token: string) => authService.verifyEmail(token);
export const changePassword = (currentPassword: string, newPassword: string) =>
  authService.changePassword(currentPassword, newPassword);
export const updateProfile = (data: Partial<User>) => authService.updateProfile(data);

// ============================================================
// Default Export
// ============================================================

export default authService;