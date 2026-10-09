// apps/frontend/web/components/auth/LoginForm.tsx

"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
//import { PasswordInput } from "@/components/auth/PasswordInput";
import { PasswordInputWithStrength } from "@/components/auth/PasswordInput";
import { useAuth } from "@/features/auth/useAuth";

interface LoginFormProps {
  onSuccess?: () => void;
  redirectTo?: string;
}

const LoadingSpinner = () => (
  <svg
    className="mr-2 h-4 w-4 animate-spin"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
  >
    <circle
      className="opacity-25"
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeWidth="4"
    />
    <path
      className="opacity-75"
      fill="currentColor"
      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
    />
  </svg>
);

export function LoginForm({ onSuccess }: LoginFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  //const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordStrength, setPasswordStrength] = useState(0);
  
   const { login, loading } = useAuth();

  const emailInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (emailInputRef.current) {
      emailInputRef.current.focus();
    }
  }, []);

  const validateEmail = (value: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!value) {
      setEmailError("Email is required");
      return false;
    }
    if (!emailRegex.test(value)) {
      setEmailError("Please enter a valid email address");
      return false;
    }
    setEmailError(null);
    return true;
  };

  const validatePassword = (value: string): boolean => {
    if (!value) {
      setPasswordError("Password is required");
      return false;
    }
    if (value.length < 8) {
      setPasswordError("Password must be at least 8 characters");
      return false;
    }
    setPasswordError(null);
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  const isEmailValid = validateEmail(email);
  const isPasswordValid = validatePassword(password);

  if (!isEmailValid || !isPasswordValid) {
    return;
  }

  setError(null);

  try {
    await login(email, password);

    onSuccess?.();

  } catch (err) {

    const message =
      err instanceof Error
        ? err.message
        : "Invalid email or password";

    setError(message);
  }
};

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setEmail(value);
    if (emailError) {
      validateEmail(value);
    }
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPassword(value);
    if (passwordError) {
      validatePassword(value);
    }
  };

  const handlePasswordStrengthChange = (strength: number) => {
    setPasswordStrength(strength);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive border border-destructive/20">
          <p className="flex items-center gap-2">
            <span>⚠️</span>
            {error}
          </p>
        </div>
      )}

      {/* Email Field */}
      <div className="space-y-2">
        <label htmlFor="email" className="text-sm font-medium leading-none">
          Email
        </label>
        <input
          ref={emailInputRef}
          id="email"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={handleEmailChange}
          onBlur={() => validateEmail(email)}
          required
          disabled={loading}
          autoFocus
          className={`flex h-10 w-full rounded-md border px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${
            emailError
              ? "border-destructive focus-visible:ring-destructive"
              : "border-input bg-background"
          }`}
        />
        {emailError && (
          <p className="text-sm text-destructive">{emailError}</p>
        )}
      </div>

      {/* Password Field */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label htmlFor="password" className="text-sm font-medium leading-none">
            Password
          </label>
          <Link
            href="/forgot-password"
            className="text-sm text-primary hover:underline"
          >
            Forgot password?
          </Link>
        </div>
        <PasswordInputWithStrength
          id="password"
          placeholder="Enter your password"
          value={password}
          onChange={handlePasswordChange}
          onBlur={() => validatePassword(password)}
          disabled={loading}
          error={passwordError || undefined}
          required
          showStrength={true}
          onStrengthChange={handlePasswordStrengthChange}
        />
        {password && password.length > 0 && !passwordError && (
          <p className="text-xs text-muted-foreground">
            Password strength: {
              passwordStrength <= 1 ? "Weak" :
              passwordStrength <= 2 ? "Fair" :
              passwordStrength <= 3 ? "Good" :
              passwordStrength <= 4 ? "Strong" :
              "Very Strong"
            }
          </p>
        )}
      </div>

      {/* Remember Me */}
      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="rememberMe"
          checked={rememberMe}
          onChange={(e) => setRememberMe(e.target.checked)}
          disabled={loading}
          className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary disabled:opacity-50"
        />
        <label htmlFor="rememberMe" className="text-sm font-normal text-muted-foreground">
          Remember me
        </label>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading}
        className="inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
      >
        {loading ? (
          <>
            <LoadingSpinner />
            Signing in...
          </>
        ) : (
          "Sign In"
        )}
      </button>

      {loading && (
        <p className="text-center text-xs text-muted-foreground animate-pulse">
          Please wait while we authenticate you...
        </p>
      )}
    </form>
  );
}