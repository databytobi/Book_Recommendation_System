// apps/frontend/web/features/auth/guard.tsx

"use client";

import { ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "./useAuth";

interface AuthGuardProps {
  children: ReactNode;
  redirectTo?: string;
}

export function AuthGuard({
  children,
  redirectTo = "/login",
}: AuthGuardProps) {

  const router = useRouter();

  const {
    isAuthenticated,
    isInitialized,
    loading,
  } = useAuth();


  useEffect(() => {

    // Wait until auth state is restored
    if (!isInitialized || loading) {
      return;
    }


    // Redirect unauthenticated users
    if (!isAuthenticated) {
      router.replace(redirectTo);
    }

  }, [
    isInitialized,
    loading,
    isAuthenticated,
    router,
    redirectTo,
  ]);


  // Loading state
  if (!isInitialized || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">

          <div className="h-10 w-10 animate-spin rounded-full border-b-2 border-primary mx-auto" />

          <p className="mt-4 text-sm text-muted-foreground">
            Checking authentication...
          </p>

        </div>
      </div>
    );
  }


  // Prevent rendering protected content
  if (!isAuthenticated) {
    return null;
  }


  return (
    <>
      {children}
    </>
  );
}


export default AuthGuard;