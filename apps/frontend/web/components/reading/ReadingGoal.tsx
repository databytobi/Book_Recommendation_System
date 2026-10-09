"use client";

import { useEffect, useState } from "react";
import {
  Award,
  BookOpen,
  Calendar,
  Star,
  Target,
  TrendingUp,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface ReadingGoalProps {
  yearlyGoal: number;
  booksRead: number;
  className?: string;
  showYearlyProgress?: boolean;
  variant?: "default" | "compact" | "detailed";
  onEditGoal?: () => void;
}

type GoalStatus =
  | "not-started"
  | "started"
  | "good"
  | "excellent"
  | "completed";

function GoalProgressBar({
  progress,
  color,
}: {
  progress: number;
  color: string;
}) {
  return (
    <div
      className="h-3 w-full overflow-hidden rounded-full bg-muted"
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={progress}
    >
      <div
        className={cn(
          "h-full rounded-full transition-all duration-700 ease-out",
          `bg-gradient-to-r ${color}`
        )}
        style={{
          width: `${Math.min(progress, 100)}%`,
        }}
      />
    </div>
  );
}

export function ReadingGoal({
  yearlyGoal,
  booksRead,
  className,
  showYearlyProgress = true,
  variant = "default",
  onEditGoal,
}: ReadingGoalProps) {
  const percentage =
    yearlyGoal > 0
      ? Math.min(Math.round((booksRead / yearlyGoal) * 100), 100)
      : 0;

  const remaining = Math.max(yearlyGoal - booksRead, 0);

  const [animatedProgress, setAnimatedProgress] = useState(0);

  useEffect(() => {
    requestAnimationFrame(() => {
      setAnimatedProgress(percentage);
    });
  }, [percentage]);

  const status: GoalStatus =
    percentage >= 100
      ? "completed"
      : percentage >= 75
      ? "excellent"
      : percentage >= 50
      ? "good"
      : percentage >= 25
      ? "started"
      : "not-started";

  const statusColor = {
    completed: "from-emerald-500 to-green-500",
    excellent: "from-blue-500 to-cyan-500",
    good: "from-primary to-violet-500",
    started: "from-amber-500 to-orange-500",
    "not-started": "from-muted to-muted",
  }[status];

  const statusMessage = {
    completed: "🎉 You've completed your reading goal!",
    excellent: "🔥 Almost there! Keep pushing!",
    good: "📚 Halfway there! You're doing great!",
    started: "💪 Nice start! Keep building momentum.",
    "not-started": "🌟 Every book counts. Let's get started!",
  }[status];

  const StatusIcon = {
    completed: Award,
    excellent: Star,
    good: TrendingUp,
    started: BookOpen,
    "not-started": Target,
  }[status];

  if (variant === "compact") {
    return (
      <div
        className={cn(
          "rounded-xl border bg-card p-4 shadow-sm",
          className
        )}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-primary/10 p-2">
              <Target className="h-4 w-4 text-primary" />
            </div>

            <div>
              <p className="text-sm font-medium">
                Reading Goal
              </p>

              <p className="text-xs text-muted-foreground">
                {booksRead} / {yearlyGoal} books
              </p>
            </div>
          </div>

          <div className="text-right">
            <p className="text-lg font-bold">
              {percentage}%
            </p>

            <div className="mt-1 w-20">
              <GoalProgressBar
                progress={animatedProgress}
                color={statusColor}
              />
            </div>
          </div>
        </div>
      </div>
    );
  }

  const content = (
    <div
      className={cn(
        "rounded-2xl border bg-card p-6 shadow-sm transition-all hover:shadow-md",
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5 text-primary" />

            <h3 className="font-semibold">
              Reading Goal
            </h3>

            <Badge
              variant={
                status === "completed"
                  ? "default"
                  : "secondary"
              }
            >
              {status === "completed"
                ? "Completed!"
                : `${percentage}%`}
            </Badge>
          </div>

          <p className="mt-1 text-sm text-muted-foreground">
            {showYearlyProgress
              ? "Track your yearly reading challenge."
              : "Your reading progress"}
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={onEditGoal}
        >
          Edit Goal
        </Button>
      </div>
            <div className="mt-6">
        {/* Main Stats */}
        <div className="flex items-end justify-between">
          <div>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold tracking-tight">
                {booksRead}
              </span>

              <span className="text-xl text-muted-foreground">
                / {yearlyGoal}
              </span>
            </div>

            <p className="mt-1 text-sm text-muted-foreground">
              Books completed
            </p>
          </div>

          <div className="rounded-xl bg-primary/10 px-4 py-3 text-center">
            <p className="text-2xl font-bold text-primary">
              {remaining}
            </p>

            <p className="text-xs text-muted-foreground">
              remaining
            </p>
          </div>
        </div>

        {/* Progress */}
        <div className="mt-6 space-y-3">
          <div className="flex justify-between text-sm">
            <span className="font-medium">
              {percentage}% complete
            </span>

            <span className="text-muted-foreground">
              {remaining} books left
            </span>
          </div>

          <GoalProgressBar
            progress={animatedProgress}
            color={statusColor}
          />

          <div className="flex justify-between text-[10px] text-muted-foreground/50">
            <span>0%</span>
            <span>25%</span>
            <span>50%</span>
            <span>75%</span>
            <span>100%</span>
          </div>
        </div>

        {/* Year Progress */}
        {showYearlyProgress && (
          <div className="mt-5 flex flex-wrap gap-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <Calendar className="h-3.5 w-3.5" />
              Year to date
            </div>

            <div className="flex items-center gap-1.5">
              <Target className="h-3.5 w-3.5" />
              Goal: {yearlyGoal} books
            </div>
          </div>
        )}

        {/* Motivation Card */}
        <div className="mt-6 flex gap-3 rounded-xl bg-muted/40 p-4">
          <div className="mt-0.5 shrink-0">
            <StatusIcon
              className={cn(
                "h-5 w-5",
                status === "completed" &&
                  "text-emerald-500",
                status === "excellent" &&
                  "text-blue-500",
                status === "good" &&
                  "text-primary",
                status === "started" &&
                  "text-amber-500",
                status === "not-started" &&
                  "text-muted-foreground"
              )}
            />
          </div>

          <div className="space-y-1">
            <p className="font-medium">
              {statusMessage}
            </p>

            <p className="text-sm text-muted-foreground">
              {status === "completed"
                ? "Amazing achievement! Set an even bigger goal for yourself."
                : `Only ${remaining} more ${
                    remaining === 1 ? "book" : "books"
                  } to reach your yearly target.`}
            </p>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="mt-5 grid grid-cols-3 gap-3">
          <div className="rounded-lg bg-muted/30 p-3 text-center">
            <p className="text-xs text-muted-foreground">
              Read
            </p>

            <p className="mt-1 text-xl font-bold">
              {booksRead}
            </p>
          </div>

          <div className="rounded-lg bg-muted/30 p-3 text-center">
            <p className="text-xs text-muted-foreground">
              Goal
            </p>

            <p className="mt-1 text-xl font-bold">
              {yearlyGoal}
            </p>
          </div>

          <div className="rounded-lg bg-muted/30 p-3 text-center">
            <p className="text-xs text-muted-foreground">
              Progress
            </p>

            <p className="mt-1 text-xl font-bold text-primary">
              {percentage}%
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  if (variant === "detailed") {
    return (
      <div
        className={cn(
          "rounded-2xl border bg-card shadow-sm",
          className
        )}
      >
        {content}
      </div>
    );
  }

  return content;
}