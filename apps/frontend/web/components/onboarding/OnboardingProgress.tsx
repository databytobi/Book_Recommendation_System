
// apps/frontend/web/components/onboarding/OnboardingProgress.tsx

"use client";

import { Check } from "lucide-react";

import { cn } from "@/lib/utils";

interface StepItem {
  id: number;
  label: string;
}

interface OnboardingProgressProps {
  currentStep: number;
  totalSteps: number;
  steps?: StepItem[];
  className?: string;
}

export function OnboardingProgress({
  currentStep,
  totalSteps,
  steps,
  className,
}: OnboardingProgressProps) {
  // Generate default step labels if none are provided
  const defaultSteps: StepItem[] = Array.from(
    { length: totalSteps },
    (_, index) => ({
      id: index + 1,
      label: `Step ${index + 1}`,
    })
  );

  const progressSteps = steps ?? defaultSteps;

  return (
    <div className={cn("w-full space-y-4", className)}>
      {/* Progress Bar */}
      <div className="relative h-2 w-full overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-primary transition-all duration-500 ease-in-out"
          style={{
            width: `${(currentStep / totalSteps) * 100}%`,
          }}
        />
      </div>

      {/* Step Indicators */}
      <div className="grid gap-4 sm:grid-cols-5">
        {progressSteps.map((step) => {
          const completed = step.id < currentStep;
          const active = step.id === currentStep;

          return (
            <div
              key={step.id}
              className="flex flex-col items-center gap-2 text-center"
            >
              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-full border-2 text-sm font-semibold transition-all duration-300",
                  completed &&
                    "border-primary bg-primary text-primary-foreground",
                  active &&
                    "border-primary bg-background text-primary ring-4 ring-primary/15",
                  !completed &&
                    !active &&
                    "border-muted-foreground/30 bg-muted text-muted-foreground"
                )}
              >
                {completed ? (
                  <Check className="h-5 w-5" />
                ) : (
                  step.id
                )}
              </div>

              <span
                className={cn(
                  "text-xs font-medium transition-colors",
                  active && "text-primary",
                  completed && "text-foreground",
                  !completed &&
                    !active &&
                    "text-muted-foreground"
                )}
              >
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export type { OnboardingProgressProps };
