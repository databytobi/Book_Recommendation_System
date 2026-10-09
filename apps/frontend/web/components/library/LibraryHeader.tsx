// apps/frontend/web/components/library/LibraryHeader.tsx

"use client";

import {
  BookOpen,
  Heart,
  CheckCircle2,
  Library,
  ArrowRight,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface LibraryHeaderProps {
  totalBooks: number;
  readingBooks: number;
  completedBooks: number;
  favoriteBooks: number;
  onBrowseBooks?: () => void;
  className?: string;
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  iconBg: string;
  iconColor: string;
}

function StatCard({
  icon,
  label,
  value,
  iconBg,
  iconColor,
}: StatCardProps) {
  return (
    <div
      className={cn(
        "group rounded-xl border bg-card p-4",
        "transition-all duration-300",
        "hover:-translate-y-1",
        "hover:shadow-lg hover:shadow-primary/5"
      )}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">
            {label}
          </p>

          <p className="mt-1 text-2xl font-bold tracking-tight">
            {value.toLocaleString()}
          </p>
        </div>

        <div
          className={cn(
            "rounded-xl p-3 transition-transform duration-300 group-hover:scale-110",
            iconBg,
            iconColor
          )}
        >
          {icon}
        </div>
      </div>
    </div>
  );
}

export function LibraryHeader({
  totalBooks,
  readingBooks,
  completedBooks,
  favoriteBooks,
  onBrowseBooks,
  className,
}: LibraryHeaderProps) {
  return (
    <section
      className={cn(
        "rounded-2xl border bg-card p-6",
        "transition-all duration-300",
        "hover:shadow-lg hover:shadow-primary/5",
        className
      )}
    >
      {/* Header */}
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-primary/10 p-3 text-primary">
              <Library className="h-6 w-6" />
            </div>

            <div>
              <h1 className="text-3xl font-bold tracking-tight">
                My Library
              </h1>

              <p className="text-sm text-muted-foreground">
                Organize your books, continue reading, and track your
                reading journey.
              </p>
            </div>
          </div>
        </div>

        <Button
          size="lg"
          onClick={onBrowseBooks}
          className="group shrink-0"
        >
          Browse Books

          <ArrowRight className="ml-2 h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" />
        </Button>
      </div>

      {/* Divider */}
      <div className="my-6 h-px bg-border" />

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Total Books"
          value={totalBooks}
          icon={
            <Library className="h-5 w-5" />
          }
          iconBg="bg-primary/10"
          iconColor="text-primary"
        />

        <StatCard
          label="Currently Reading"
          value={readingBooks}
          icon={
            <BookOpen className="h-5 w-5" />
          }
          iconBg="bg-blue-500/10"
          iconColor="text-blue-600"
        />

        <StatCard
          label="Completed"
          value={completedBooks}
          icon={
            <CheckCircle2 className="h-5 w-5" />
          }
          iconBg="bg-emerald-500/10"
          iconColor="text-emerald-600"
        />

        <StatCard
          label="Favorites"
          value={favoriteBooks}
          icon={
            <Heart className="h-5 w-5 fill-current" />
          }
          iconBg="bg-rose-500/10"
          iconColor="text-rose-500"
        />
      </div>
    </section>
  );
}

export type { LibraryHeaderProps };