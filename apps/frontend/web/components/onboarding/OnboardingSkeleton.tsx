
// apps/frontend/web/components/onboarding/OnboardingSkeleton.tsx

"use client";

import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface OnboardingSkeletonProps {
  className?: string;
  showProgress?: boolean;
  cards?: number;
}

export function OnboardingSkeleton({
  className,
  showProgress = true,
  cards = 6,
}: OnboardingSkeletonProps) {
  return (
    <div
      className={cn(
        "mx-auto flex w-full max-w-6xl flex-col space-y-8",
        className
      )}
    >
      {/* Progress */}
      {showProgress && (
        <div className="space-y-4">
          <Skeleton className="h-3 w-full rounded-full" />

          <div className="flex items-center justify-between">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-4 w-16" />
          </div>
        </div>
      )}

      {/* Header */}
      <div className="space-y-4 text-center">
        <Skeleton className="mx-auto h-16 w-16 rounded-full" />

        <Skeleton className="mx-auto h-8 w-80" />

        <Skeleton className="mx-auto h-4 w-[420px]" />
      </div>

      {/* Selection Grid */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: cards }).map((_, index) => (
          <div
            key={index}
            className="rounded-2xl border bg-card p-5"
          >
            <div className="flex items-start gap-4">
              <Skeleton className="h-16 w-16 rounded-full" />

              <div className="flex-1 space-y-3">
                <Skeleton className="h-5 w-32" />

                <Skeleton className="h-4 w-full" />

                <Skeleton className="h-4 w-3/4" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between border-t pt-6">
        <Skeleton className="h-10 w-28 rounded-lg" />

        <Skeleton className="h-10 w-36 rounded-lg" />
      </div>
    </div>
  );
}

export default OnboardingSkeleton;
