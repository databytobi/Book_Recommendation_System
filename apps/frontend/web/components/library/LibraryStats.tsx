
// apps/frontend/web/components/library/LibraryStats.tsx

"use client";

import {
  BookOpen,
  CheckCircle2,
  Clock3,
  Heart,
  TrendingUp,
  Trophy,
} from "lucide-react";

import { cn } from "@/lib/utils";

interface LibraryStatsProps {
  totalBooks: number;
  readingBooks: number;
  completedBooks: number;
  favoriteBooks: number;
  pagesRead?: number;
  averageRating?: number;
  className?: string;
}

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  iconColor: string;
  iconBg: string;
}

function StatCard({
  title,
  value,
  subtitle,
  icon,
  iconBg,
  iconColor,
}: StatCardProps) {
  return (
    <div
      className={cn(
        "group rounded-2xl border bg-card p-5",
        "transition-all duration-300",
        "hover:-translate-y-1",
        "hover:shadow-lg hover:shadow-primary/5"
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground">
            {title}
          </p>

          <h3 className="mt-2 text-3xl font-bold tracking-tight">
            {value}
          </h3>

          {subtitle && (
            <p className="mt-1 text-xs text-muted-foreground">
              {subtitle}
            </p>
          )}
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

export function LibraryStats({
  totalBooks,
  readingBooks,
  completedBooks,
  favoriteBooks,
  pagesRead = 0,
  averageRating = 0,
  className,
}: LibraryStatsProps) {
  const completionRate =
    totalBooks > 0
      ? Math.round((completedBooks / totalBooks) * 100)
      : 0;

  return (
    <section
      className={cn(
        "space-y-6",
        className
      )}
    >
      {/* Heading */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight">
          Reading Statistics
        </h2>

        <p className="text-sm text-muted-foreground">
          A quick overview of your reading journey.
        </p>
      </div>

      {/* Stats Grid */}
      <div
        className="
          grid
          gap-5
          sm:grid-cols-2
          xl:grid-cols-3
        "
      >
        <StatCard
          title="Books Read"
          value={completedBooks}
          subtitle={`${completionRate}% completion`}
          icon={<CheckCircle2 className="h-5 w-5" />}
          iconBg="bg-emerald-500/10"
          iconColor="text-emerald-600"
        />

        <StatCard
          title="Currently Reading"
          value={readingBooks}
          subtitle="Books in progress"
          icon={<BookOpen className="h-5 w-5" />}
          iconBg="bg-blue-500/10"
          iconColor="text-blue-600"
        />

        <StatCard
          title="Favorites"
          value={favoriteBooks}
          subtitle="Books you loved"
          icon={<Heart className="h-5 w-5 fill-current" />}
          iconBg="bg-rose-500/10"
          iconColor="text-rose-500"
        />

        <StatCard
          title="Pages Read"
          value={pagesRead.toLocaleString()}
          subtitle="Across your library"
          icon={<Clock3 className="h-5 w-5" />}
          iconBg="bg-violet-500/10"
          iconColor="text-violet-600"
        />

        <StatCard
          title="Average Rating"
          value={averageRating.toFixed(1)}
          subtitle="Your library average"
          icon={<TrendingUp className="h-5 w-5" />}
          iconBg="bg-amber-500/10"
          iconColor="text-amber-600"
        />

        <StatCard
          title="Library Size"
          value={totalBooks}
          subtitle="Books collected"
          icon={<Trophy className="h-5 w-5" />}
          iconBg="bg-primary/10"
          iconColor="text-primary"
        />
      </div>
    </section>
  );
}

export type { LibraryStatsProps };
