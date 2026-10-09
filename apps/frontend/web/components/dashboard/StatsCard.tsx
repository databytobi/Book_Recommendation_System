// apps/frontend/web/components/dashboard/StatsCard.tsx

import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: ReactNode;

  description?: string;
  trend?: string;
  loading?: boolean;
  className?: string;
  iconClassName?: string;
  onClick?: () => void;
}

export function StatsCard({
  title,
  value,
  icon,
  description,
  trend,
  loading = false,
  className,
  iconClassName,
  onClick,
}: StatsCardProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        "group relative overflow-hidden rounded-xl border border-border/50 bg-card",
        "p-5 transition-all duration-300",
        "hover:-translate-y-1 hover:border-primary/20 hover:shadow-lg",
        onClick && "cursor-pointer",
        className
      )}
    >
      {/* subtle gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-primary/[0.03] pointer-events-none" />

      <div className="relative flex items-start justify-between">
        <div className="space-y-3 flex-1">

          {/* Title */}
          <p className="text-sm font-medium text-muted-foreground">
            {title}
          </p>

          {/* Value */}
          {loading ? (
            <div className="h-9 w-20 animate-pulse rounded-md bg-muted" />
          ) : (
            <h2 className="text-3xl font-bold tracking-tight text-foreground">
              {value}
            </h2>
          )}

          {/* Trend + Description */}
          <div className="flex flex-wrap items-center gap-2">

            {trend && (
              <span
                className={cn(
                  "inline-flex items-center rounded-full px-2.5 py-1",
                  "text-xs font-semibold",
                  trend.startsWith("+")
                    ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                    : "bg-red-500/10 text-red-600 dark:text-red-400"
                )}
              >
                {trend}
              </span>
            )}

            {description && (
              <p className="text-xs text-muted-foreground">
                {description}
              </p>
            )}

          </div>
        </div>

        {/* Icon */}
        <div
          className={cn(
            "flex h-12 w-12 items-center justify-center",
            "rounded-xl border border-primary/10",
            "bg-primary/5 text-primary",
            "transition-all duration-300",
            "group-hover:scale-110",
            "group-hover:bg-primary",
            "group-hover:text-primary-foreground",
            iconClassName
          )}
        >
          {icon}
        </div>
      </div>
    </div>
  );
}