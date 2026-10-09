// apps/frontend/web/features/auth/provider.tsx

"use client";

import { ReactNode, useMemo, useState, useEffect, useCallback } from "react";
import { useRouter, usePathname } from "next/navigation";

import { AuthContext } from "./context";
import type { User, RegisterRequest, AuthError, AuthContextType } from "./types";
import { authService } from "./service";
import { tokenStorage } from "@/services/storage/token";
import { getOnboardingStatus } from "@/lib/api/onboarding";

interface AuthProviderProps {
  children: ReactNode;
  redirectTo?: string;
  redirectIfAuthenticated?: string;
}

export function AuthProvider({ 
  children, 
  redirectTo = "/login",
  redirectIfAuthenticated = "/dashboard" 
}: AuthProviderProps) {
  const router = useRouter();
  const pathname = usePathname();
  
  // ==========================
  // State
  // ==========================
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<AuthError | null>(null);

  // ==========================
  // Derived State
  // ==========================
  const isAuthenticated = !!user;

  // ==========================
  // Helper Functions
  // ==========================
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // ==========================
  // Auth Functions
  // ==========================
  
  const initializeAuth = useCallback(async () => {
    try {
      setLoading(true);
      const token = tokenStorage.getAccessToken();
      
      if (!token) {
        setIsInitialized(true);
        setLoading(false);
        return;
      }

      if (tokenStorage.isExpired()) {
        tokenStorage.clear();
        setIsInitialized(true);
        setLoading(false);
        return;
      }

      const userData = await authService.getCurrentUser();
      setUser(userData);
      setIsInitialized(true);
    } catch {
      tokenStorage.clear();
      setUser(null);
      setIsInitialized(true);
    } finally {
      setLoading(false);
    }
  }, []);

  const login = useCallback(
  async (email: string, password: string) => {

    try {

      setLoading(true);
      setError(null);


      const response =
        await authService.login({
          email,
          password,
        });


      // Store authentication tokens
      tokenStorage.setTokens(
        response.access_token,
        response.refresh_token,
        response.expires_in
      );


      // Store authenticated user
      setUser(response.user);

      try {
        const onboardingStatus = await getOnboardingStatus();

        if (onboardingStatus.is_complete) {
          router.push("/dashboard");
        } else {
          router.push("/onboarding");
        }
      } catch (onboardingError) {
        console.error(
          "Failed to check onboarding status:",
          onboardingError
        );

        // If onboarding status cannot be determined,
        // keep the user on the dashboard rather than
        // blocking authentication.
        router.push(redirectIfAuthenticated);
      }


    } catch (err) {

      const authError =
        err as AuthError;

      setError(authError);

      throw authError;


    } finally {

      setLoading(false);

    }

  },
  [
    router,
    redirectIfAuthenticated,
  ]
);

  const register = useCallback(async (data: RegisterRequest) => {
    try {
      setLoading(true);
      setError(null);

      await authService.register(data);
      router.push(`${redirectTo}?registered=true`);
    } catch (err) {
      const authError = err as AuthError;
      setError(authError);
      throw authError;
    } finally {
      setLoading(false);
    }
  }, [router, redirectTo]);

  const logout = useCallback(async () => {
  try {
    setLoading(true);

    // FIX 5: Add catch to suppress unhandled promise rejection warning
    await authService.logout().catch(() => {});

  } catch {

    console.error("Logout error:");

  } finally {

    // Remove tokens from storage
    tokenStorage.clear();

    // Clear user state
    setUser(null);

    setLoading(false);

    // Return to login
    router.replace(redirectTo);
  }

}, [router, redirectTo]);

  // FIX 2: Simplify refreshUser - keep implementation, add void when calling elsewhere
  const refreshUser = useCallback(async () => {
    try {
      setLoading(true);
      const userData = await authService.getCurrentUser();
      setUser(userData);
    } catch (err) {
      const authError = err as AuthError;
      setError(authError);
      
      if (authError.status === 401) {
        tokenStorage.clear();
        setUser(null);
        router.push(redirectTo);
      }
      
      throw authError;
    } finally {
      setLoading(false);
    }
  }, [router, redirectTo]);

  const updateUser = useCallback((userData: User) => {
    setUser(userData);
  }, []);

  const hasRole = useCallback((role: string): boolean => {
    if (!user) return false;
    return user.roles?.includes(role) || false;
  }, [user]);

  const isAdmin = useCallback((): boolean => {
    return hasRole("admin") || hasRole("superuser");
  }, [hasRole]);

  // ==========================
  // 🔥 REDIRECT LOGIC - FIXED
  // ==========================
  useEffect(() => {
    // Don't redirect until initialization is complete
    if (!isInitialized) return;

    const isAuthPage = pathname === "/login" || pathname === "/register";
    const isHomePage = pathname === "/";
    const isPublicPage = isAuthPage || isHomePage;

    // FIX 3: Removed debug console.log statements

    // FIX 4: Simplified redirect logic
    // Case 1 & 3: User is authenticated and on auth page OR home page -> redirect to dashboard
    if (isAuthenticated && (isAuthPage || isHomePage)) {
      router.replace(redirectIfAuthenticated);
      return;
    }

    // Case 2: User is NOT authenticated and NOT on public page -> redirect to login
    if (!isAuthenticated && !isPublicPage) {
      router.replace(redirectTo);
      return;
    }

    // Case 4: User is NOT authenticated and on auth page -> stay (allow login/register)
    // Case 5: User is authenticated and on protected page -> stay (allow access)

  }, [isInitialized, isAuthenticated, pathname, router, redirectTo, redirectIfAuthenticated]);

  // ==========================
  // Initialize Auth
  // ==========================
  // FIX 1: Add void to initializeAuth
  useEffect(() => {
    let isMounted = true;
    
    const init = async () => {
      if (isMounted) {
        await initializeAuth();
      }
    };
    
    init();
    
    return () => {
      isMounted = false;
    };
  }, [initializeAuth]);

  // ==========================
  // Context Value
  // ==========================
  const value = useMemo<AuthContextType>(
    () => ({
      user,
      loading,
      isAuthenticated,
      isInitialized,
      error,
      login,
      register,
      logout,
      refreshUser,
      updateUser,
      clearError,
      hasRole,
      isAdmin,
    }),
    [
      user,
      loading,
      isAuthenticated,
      isInitialized,
      error,
      login,
      register,
      logout,
      refreshUser,
      updateUser,
      clearError,
      hasRole,
      isAdmin,
    ]
  );

  // ==========================
  // Loading State
  // ==========================
  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // ==========================
  // Provider
  // ==========================
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export default AuthProvider;