// apps/frontend/web/components/onboarding/WelcomeStep.tsx

"use client";

import { BookOpen, Sparkles, Brain, ArrowRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface WelcomeStepProps {
  onStart: () => void;
  className?: string;
  userName?: string;
}

export function WelcomeStep({
  onStart,
  className,
  userName,
}: WelcomeStepProps) {
  return (
    <div
      className={cn(
        "mx-auto flex w-full max-w-4xl flex-col items-center text-center",
        className
      )}
    >
      {/* Hero Icon */}
      <div className="mb-8 flex h-24 w-24 items-center justify-center rounded-full bg-primary/10">
        <BookOpen className="h-12 w-12 text-primary" />
      </div>

      {/* Heading */}
      <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
        {userName
          ? `Welcome, ${userName}!`
          : "Welcome to Your Library"}
      </h1>

      <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
        {/* FIX: Replaced ' with &apos; */}
        Let&apos;s personalize your reading experience.
        In the next few steps you&apos;ll tell us about the books and authors you
        enjoy so we can recommend titles you&apos;ll actually love.
      </p>

      {/* Features */}
      <div className="mt-12 grid w-full gap-6 md:grid-cols-3">
        <div className="rounded-2xl border bg-card p-6 text-left transition-all hover:border-primary/30 hover:shadow-md">
          <Sparkles className="mb-4 h-10 w-10 text-primary" />

          <h3 className="font-semibold">
            Personalized Recommendations
          </h3>

          <p className="mt-2 text-sm text-muted-foreground leading-6">
            Discover books based on your favorite authors,
            genres, and reading interests.
          </p>
        </div>

        <div className="rounded-2xl border bg-card p-6 text-left transition-all hover:border-primary/30 hover:shadow-md">
          <Brain className="mb-4 h-10 w-10 text-primary" />

          <h3 className="font-semibold">
            AI-Powered Suggestions
          </h3>

          <p className="mt-2 text-sm text-muted-foreground leading-6">
            Our recommendation engine learns your preferences
            to deliver increasingly relevant books.
          </p>
        </div>

        <div className="rounded-2xl border bg-card p-6 text-left transition-all hover:border-primary/30 hover:shadow-md">
          <BookOpen className="mb-4 h-10 w-10 text-primary" />

          <h3 className="font-semibold">
            Build Your Library
          </h3>

          <p className="mt-2 text-sm text-muted-foreground leading-6">
            Save books, track your reading progress,
            and organize your personal collection.
          </p>
        </div>
      </div>

      {/* Estimated Time */}
      <div className="mt-10 rounded-full bg-muted px-5 py-2 text-sm text-muted-foreground">
        ⏱ Takes about 2–3 minutes
      </div>

      {/* CTA */}
      <Button
        size="lg"
        className="mt-10 min-w-[220px] gap-2"
        onClick={onStart}
      >
        Get Started
        <ArrowRight className="h-4 w-4" />
      </Button>
    </div>
  );
}

export type { WelcomeStepProps };