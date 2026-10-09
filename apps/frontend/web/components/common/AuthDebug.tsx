"use client";

import { useAuth } from "@/features/auth/hooks";

export function AuthDebug() {
  const {
    user,
    loading,
    isAuthenticated,
  } = useAuth();

  return (
    <div className="rounded-lg border p-4">
      <h2>Authentication Status</h2>

      <p>Loading: {loading ? "Yes" : "No"}</p>

      <p>
        Authenticated:
        {isAuthenticated ? " Yes" : " No"}
      </p>

      <pre>
        {JSON.stringify(user, null, 2)}
      </pre>
    </div>
  );
}