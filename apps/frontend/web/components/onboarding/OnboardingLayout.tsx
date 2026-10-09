
// apps/frontend/web/components/onboarding/OnboardingLayout.tsx

"use client";

import { ReactNode } from "react";
import { ArrowLeft, ArrowRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface OnboardingLayoutProps {
  children: ReactNode;

  title: string;
  description?: string;

  currentStep: number;
  totalSteps: number;

  progress?: ReactNode;

  onNext?: () => void;
  onBack?: () => void;
  onSkip?: () => void;

  nextLabel?: string;
  backLabel?: string;
  skipLabel?: string;

  nextDisabled?: boolean;
  backDisabled?: boolean;
  loading?: boolean;

  className?: string;

  footer?: ReactNode;
}

export function OnboardingLayout({
  children,
  title,
  description,
  currentStep,
  totalSteps,
  progress,

  onNext,
  onBack,
  onSkip,

  nextLabel = "Continue",
  backLabel = "Back",
  skipLabel = "Skip",

  nextDisabled = false,
  backDisabled = false,
  loading = false,

  className,
  footer,
}: OnboardingLayoutProps) {
  return (
    <div
      className={cn(
        "min-h-screen bg-background",
        className
      )}
    >
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-6 py-10">

        {/* Top */}
        <header className="space-y-6">

          <div className="flex items-center justify-between">

            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Step {currentStep} of {totalSteps}
              </p>

              <h1 className="mt-2 text-3xl font-bold tracking-tight">
                {title}
              </h1>

              {description && (
                <p className="mt-2 max-w-2xl text-muted-foreground">
                  {description}
                </p>
              )}
            </div>

            {onSkip && (
              <Button
                variant="ghost"
                onClick={onSkip}
              >
                {skipLabel}
              </Button>
            )}
          </div>

          {progress}
        </header>

        {/* Content */}
        <main className="flex flex-1 items-center py-10">
          <div className="w-full">
            {children}
          </div>
        </main>

        {/* Footer */}
        <footer className="space-y-6 border-t pt-6">

          {footer}

          <div className="flex items-center justify-between">

            <Button
              variant="outline"
              onClick={onBack}
              disabled={backDisabled || loading}
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              {backLabel}
            </Button>

            <Button
              onClick={onNext}
              disabled={nextDisabled || loading}
            >
              {loading ? "Saving..." : nextLabel}

              {!loading && (
                <ArrowRight className="ml-2 h-4 w-4" />
              )}
            </Button>

          </div>

        </footer>

      </div>
    </div>
  );
}

export type { OnboardingLayoutProps };
