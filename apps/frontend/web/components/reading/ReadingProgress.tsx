"use client";

import { BookOpen, CheckCircle, Clock, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface ReadingProgressProps {
  progress: number;
  currentPage: number;
  totalPages: number;
  className?: string;
  showLabel?: boolean;
  variant?: "default" | "compact" | "detailed";
  estimatedTimeLeft?: string;
  lastReadAt?: string;
  animated?: boolean;
}

type ReadingStatus =
  | "not-started"
  | "reading"
  | "completed";

interface ProgressBarProps {
  progress: number;
  status: ReadingStatus;
  animated?: boolean;
  height?: string;
}

function ProgressBar({
  progress,
  status,
  animated = true,
  height = "h-2",
}: ProgressBarProps) {
  const color =
    status === "completed"
      ? "from-emerald-500 to-green-500"
      : status === "reading"
      ? "from-primary to-violet-500"
      : "from-muted to-muted";

  return (
    <div
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={progress}
      className={cn(
        "w-full overflow-hidden rounded-full bg-muted",
        height
      )}
    >
      <div
        className={cn(
          "h-full rounded-full bg-gradient-to-r",
          color,
          animated && "transition-all duration-700 ease-out"
        )}
        style={{
          width: `${progress}%`,
        }}
      />
    </div>
  );
}

export function ReadingProgress({
  progress,
  currentPage,
  totalPages,
  className,
  showLabel = true,
  variant = "default",
  estimatedTimeLeft,
  lastReadAt,
  animated = true,
}: ReadingProgressProps) {
  const clampedProgress = Math.min(Math.max(progress, 0), 100);

  const status: ReadingStatus =
    clampedProgress >= 100
      ? "completed"
      : clampedProgress > 0
      ? "reading"
      : "not-started";

  const statusText =
    status === "completed"
      ? "Completed!"
      : status === "reading"
      ? `${clampedProgress}% complete`
      : "Not started";

  // ============================================================
  // Compact Variant
  // ============================================================

  if (variant === "compact") {
    return (
      <div className={cn("flex items-center gap-3", className)}>
        <div className="flex-1">
          <ProgressBar
            progress={clampedProgress}
            status={status}
            animated={animated}
            height="h-1.5"
          />
        </div>

        <span className="min-w-[40px] text-right text-xs font-medium tabular-nums text-muted-foreground">
          {clampedProgress}%
        </span>
      </div>
    );
  }

  // ============================================================
  // Detailed Variant
  // ============================================================

  if (variant === "detailed") {
    return (
      <div
        className={cn(
          "space-y-4 rounded-xl border bg-card p-5",
          className
        )}
      >
        <div className="flex items-start justify-between">
          <div>
            <h4 className="font-medium">
              Reading Progress
            </h4>

            <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
              <BookOpen className="h-4 w-4" />
              {currentPage.toLocaleString()} of{" "}
              {totalPages.toLocaleString()} pages
            </div>
          </div>

          <div className="text-right">
            <div className="text-3xl font-bold tabular-nums">
              {clampedProgress}%
            </div>

            <div className="text-xs text-muted-foreground">
              {statusText}
            </div>
          </div>
        </div>

        <ProgressBar
          progress={clampedProgress}
          status={status}
          animated={animated}
          height="h-3"
        />
                <div className="grid gap-3 border-t pt-4 text-sm text-muted-foreground sm:grid-cols-2">
          <div className="flex items-center gap-2">
            {status === "completed" ? (
              <>
                <CheckCircle className="h-4 w-4 text-emerald-500" />
                <span>Completed</span>
              </>
            ) : (
              <>
                <TrendingUp className="h-4 w-4 text-primary" />
                <span>{statusText}</span>
              </>
            )}
          </div>

          {estimatedTimeLeft && status !== "completed" && (
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              <span>~{estimatedTimeLeft} remaining</span>
            </div>
          )}

          {lastReadAt && (
            <div className="flex items-center gap-2 sm:col-span-2">
              <Clock className="h-4 w-4" />
              <span>
                Last read{" "}
                {new Date(lastReadAt).toLocaleDateString()}
              </span>
            </div>
          )}
        </div>
      </div>
    );
  }

  // ============================================================
  // Default Variant
  // ============================================================

  return (
    <TooltipProvider>
      <div className={cn("space-y-2", className)}>
        {showLabel && (
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <div className="flex items-center gap-2">
              <BookOpen className="h-3.5 w-3.5" />
              <span>
                {currentPage.toLocaleString()} /{" "}
                {totalPages.toLocaleString()} pages
              </span>
            </div>

            <Tooltip>
              <TooltipTrigger>
                <button
                 type="button"
                 className={cn(
                "font-medium tabular-nums",
                status === "completed" &&
                "text-emerald-600 dark:text-emerald-400"
                )}
               >
                {clampedProgress}% 
                </button>
                </TooltipTrigger> 

              <TooltipContent side="left">
                <p>{statusText}</p>

                {estimatedTimeLeft &&
                  status !== "completed" && (
                    <p className="text-xs text-muted-foreground">
                      {estimatedTimeLeft} remaining
                    </p>
                  )}
              </TooltipContent>
            </Tooltip>
          </div>
        )}

        <ProgressBar
          progress={clampedProgress}
          status={status}
          animated={animated}
        />

        {status === "completed" && (
          <div className="flex items-center gap-1.5 text-xs text-emerald-600 dark:text-emerald-400">
            <CheckCircle className="h-3.5 w-3.5" />
            <span>Book completed!</span>
          </div>
        )}

        {lastReadAt && status !== "completed" && (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            <span>
              Updated{" "}
              {new Date(lastReadAt).toLocaleDateString()}
            </span>
          </div>
        )}
      </div>
    </TooltipProvider>
  );
}