// apps/frontend/web/components/dashboard/WelcomeCard.tsx

"use client";

import Link from "next/link";
import { useAuth } from "@/features/auth/useAuth";
import { format } from "date-fns";
import {
  CalendarDays,
  Sparkles,
  TrendingUp,
  BookOpen,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

// FIX 1: Updated interface with real data props
interface WelcomeCardProps {
  className?: string;
  showDate?: boolean;
  showStats?: boolean;
  showAction?: boolean;

  booksRead?: number;
  streak?: number;
  queue?: number;
}

// FIX 2: Updated component parameters with new props
export function WelcomeCard({
  className,
  showDate = true,
  showStats = true,
  showAction = true,
  booksRead = 0,
  streak = 0,
  queue = 0,
}: WelcomeCardProps) {
  const { user } = useAuth();

  const displayName =
    user?.full_name ||
    user?.username ||
    "Reader";

  const greeting = (() => {
    const hour = new Date().getHours();

    if (hour < 12) return "Good morning";
    if (hour < 17) return "Good afternoon";

    return "Good evening";
  })();

  // FIX 3: Replace stats array with real data
  const stats = [
    {
      label: "Books Read",
      value: String(booksRead),
      icon: BookOpen,
    },
    {
      label: "Streak",
      value: `${streak} Days`,
      icon: TrendingUp,
    },
    {
      label: "Queue",
      value: String(queue),
      icon: Sparkles,
    },
  ];

  return (
    <section
      className={cn(
        "relative overflow-hidden rounded-xl border border-border/50",
        "bg-gradient-to-br from-card via-card to-primary/[0.03]",
        "p-6 lg:p-7",
        "shadow-sm transition-all duration-300",
        "hover:shadow-md",
        className
      )}
    >
      {/* Decorative background */}
      <div className="absolute right-0 top-0 h-56 w-56 rounded-full bg-primary/5 blur-3xl" />
      <div className="absolute bottom-0 left-0 h-40 w-40 rounded-full bg-primary/5 blur-3xl" />

      <div className="relative z-10">

        {/* Header */}
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">

          <div className="space-y-2">

            <div className="flex items-center gap-2">

              <p className="text-sm font-medium text-muted-foreground">
                {greeting}
              </p>

              <Badge
                variant="outline"
                className="gap-2"
              >
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                Online
              </Badge>

            </div>

            <h1 className="text-2xl font-bold tracking-tight lg:text-3xl">
              Welcome back{" "}
              <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">
                {displayName}
              </span>
              👋
            </h1>

            <p className="max-w-xl text-sm text-muted-foreground">
              Continue your reading journey and discover books
              selected specifically for you.
            </p>

          </div>

          {showDate && (
            <div className="flex items-center gap-2 rounded-lg border bg-background/60 px-4 py-2 text-sm text-muted-foreground backdrop-blur">
              <CalendarDays className="h-4 w-4" />
              {format(new Date(), "EEEE, MMM d")}
            </div>
          )}

        </div>

        {/* Stats */}
        {showStats && (
          <div className="mt-6 grid grid-cols-3 gap-3">

            {stats.map((item) => {
              const Icon = item.icon;

              return (
                <div
                  key={item.label}
                  className="rounded-lg border bg-background/60 p-4 backdrop-blur"
                >
                  <div className="mb-2 flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <Icon className="h-4 w-4" />
                  </div>

                  <p className="text-xl font-bold">
                    {item.value}
                  </p>

                  <p className="text-xs text-muted-foreground">
                    {item.label}
                  </p>
                </div>
              );
            })}

          </div>
        )}

        {/* Actions */}
        {showAction && (
          <div className="mt-6 flex flex-wrap gap-3">

            <Button>
              {/* FIX 4: Updated Discover Books navigation */}
              <Link
                href="/dashboard/discover"
                className="flex items-center gap-2"
              >
                <Sparkles className="h-4 w-4" />
                Discover Books
              </Link>
            </Button>

            <Button variant="outline">
              <Link
                href="/dashboard/library"
                className="flex items-center gap-2"
              >
                <BookOpen className="h-4 w-4" />
                My Library
              </Link>
            </Button>

          </div>
        )}

      </div>
    </section>
  );
}