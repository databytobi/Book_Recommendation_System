// apps/frontend/web/app/(auth)/layout.tsx

import type { ReactNode } from "react";
import { AuthHero } from "@/components/auth/AuthHero";

interface AuthLayoutProps {
  children: ReactNode;
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl">
        {/* Left Panel - Auth Hero (Desktop Only) */}
        <section className="hidden lg:flex lg:w-1/2 flex-col justify-between bg-gradient-to-br from-indigo-600 via-indigo-700 to-violet-700 p-8 lg:p-12 text-white relative overflow-hidden">
          {/* Decorative Background Elements */}
          <div className="absolute -top-24 -right-24 h-64 w-64 rounded-full bg-white/5 blur-3xl" />
          <div className="absolute -bottom-32 -left-32 h-80 w-80 rounded-full bg-white/5 blur-3xl" />
          
          {/* Top Section - Branding */}
          <div className="relative z-10 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-white/20 backdrop-blur-sm flex items-center justify-center shadow-lg">
                <span className="text-xl font-bold">📚</span>
              </div>
              <div>
                <span className="text-lg font-semibold tracking-tight">
                  BookRec
                </span>
                <p className="text-xs text-white/60 hidden sm:block">
                  Recommendation System
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-white/50 hidden md:inline">
                v1.0.0
              </span>
            </div>
          </div>

          {/* Hero Content */}
          <div className="relative z-10 py-8">
            <AuthHero />
          </div>

          {/* Bottom Section */}
          <div className="relative z-10 flex flex-col sm:flex-row items-center justify-between gap-2 text-sm text-white/50">
            <p>&copy; {new Date().getFullYear()} Book Recommendation System</p>
            <div className="flex items-center gap-4">
              <a href="/privacy" className="hover:text-white/80 transition-colors">
                Privacy
              </a>
              <a href="/terms" className="hover:text-white/80 transition-colors">
                Terms
              </a>
              <a href="/about" className="hover:text-white/80 transition-colors">
                About
              </a>
            </div>
          </div>
        </section>

        {/* Right Panel - Auth Form */}
        <section className="relative flex w-full items-center justify-center p-6 sm:p-10 lg:w-1/2">
          <div className="w-full max-w-md">
            {children}
          </div>
        </section>
      </div>
    </main>
  );
}