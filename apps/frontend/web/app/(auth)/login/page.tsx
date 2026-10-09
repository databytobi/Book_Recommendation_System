// apps/frontend/web/app/(auth)/login/page.tsx

import type { Metadata } from "next";
import Link from "next/link";
import { AuthCard } from "@/components/auth/AuthCard";
import { LoginForm } from "@/components/auth/LoginForm";
import { SocialLoginButtons } from "@/components/auth/SocialLoginButtons";

//import { AuthCard, LoginForm, SocialLoginButtons } from "@/components/auth";

export const metadata: Metadata = {
  title: "Sign In | Book Recommendation System",
  description: "Sign in to your account to discover personalized book recommendations",
};

export default function LoginPage() {
  return (
    <AuthCard
      title="Welcome back"
      description="Sign in to continue your reading journey"
    >
      {/* Login Form */}
      <LoginForm />

      {/* Divider */}
      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t border-border" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-card px-2 text-muted-foreground">
            Or continue with
          </span>
        </div>
      </div>

      {/* Social Login Buttons */}
      <SocialLoginButtons />

      {/* Sign Up Link */}
      <p className="mt-6 text-center text-sm text-muted-foreground">
        {/* FIX: Replaced ' with &apos; */}
        Don&apos;t have an account?{" "}
        <Link
          href="/register"
          className="font-medium text-primary hover:text-primary/90 hover:underline transition-colors"
        >
          Create one now
        </Link>
      </p>
    </AuthCard>
  );
}