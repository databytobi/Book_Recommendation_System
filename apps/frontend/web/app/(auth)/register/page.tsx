// apps/frontend/web/app/(auth)/register/page.tsx

import type { Metadata } from "next";
import Link from "next/link";
import { AuthCard } from "@/components/auth/AuthCard";
import { RegisterForm } from "@/components/auth/RegisterForm";
import { SocialLoginButtons } from "@/components/auth/SocialLoginButtons";

export const metadata: Metadata = {
  title: "Sign Up | Book Recommendation System",
  description: "Create your account to discover personalized book recommendations",
};

export default function RegisterPage() {
  return (
    <AuthCard
      title="Create an account"
      description="Start your reading journey today"
    >
      {/* Register Form */}
      <RegisterForm />

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

      {/* Sign In Link */}
      <p className="mt-6 text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link
          href="/login"
          className="font-medium text-primary hover:text-primary/90 hover:underline transition-colors"
        >
          Sign in
        </Link>
      </p>
    </AuthCard>
  );
}