// apps/frontend/web/components/onboarding/CompletionStep.tsx

"use client";

import { CheckCircle2, Sparkles, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface CompletionStepProps {
  loading?: boolean;
  error?: string | null;
  onFinish: () => void;
  className?: string;
}

export function CompletionStep({
  loading = false,
  error = null,
  onFinish,
  className,
}: CompletionStepProps) {
  return (
    <div
      className={cn(
        "mx-auto flex max-w-2xl flex-col items-center text-center",
        "space-y-8 py-10",
        className
      )}
    >
      {/* Success Icon */}
      <div className="relative">
        <div className="absolute inset-0 rounded-full bg-primary/20 blur-2xl" />

        <div className="relative flex h-28 w-28 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-xl">
          <CheckCircle2 className="h-14 w-14" />
        </div>
      </div>

      {/* Heading */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 rounded-full border bg-primary/5 px-4 py-1 text-sm font-medium text-primary">
          <Sparkles className="h-4 w-4" />
          Your profile is ready
        </div>

        <h1 className="text-4xl font-bold tracking-tight">
          Welcome to Your Personal Library
        </h1>

        <p className="mx-auto max-w-xl text-muted-foreground">
          {/* FIX: Replaced ' with &apos; */}
          We&apos;ve saved your preferences and will now personalize your book
          recommendations, homepage, and reading experience.
        </p>
      </div>

      {/* What's Next */}
      <div className="w-full rounded-2xl border bg-card p-6 text-left">
        <h2 className="mb-4 text-lg font-semibold">
          Here&apos;s what happens next
        </h2>

        <ul className="space-y-3 text-sm text-muted-foreground">
          <li className="flex items-start gap-3">
            <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
            Personalized recommendations will appear on your dashboard.
          </li>

          <li className="flex items-start gap-3">
            <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
            Books matching your favorite genres and authors will be prioritized.
          </li>

          <li className="flex items-start gap-3">
            <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
            Your reading preferences will improve future recommendations.
          </li>

          <li className="flex items-start gap-3">
            <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
            You can update these preferences anytime from Settings.
          </li>
        </ul>
      </div>

      {/* Error */}
      {error && (
        <div className="w-full rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
          {error}
        </div>
      )}

      {/* Finish */}
      <Button
        size="lg"
        disabled={loading}
        onClick={onFinish}
        className="min-w-[240px]"
      >
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Finishing Setup...
          </>
        ) : (
          "Go to My Dashboard"
        )}
      </Button>
    </div>
  );
}

export type { CompletionStepProps };