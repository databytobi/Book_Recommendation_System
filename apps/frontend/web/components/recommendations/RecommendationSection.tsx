// apps/frontend/web/components/recommendations/RecommendationSection.tsx

"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import {
  Sparkles,
  ArrowRight,
  ChevronRight,
  Clock,
  Zap,
} from "lucide-react";

import { cn } from "@/lib/utils";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

interface RecommendationSectionProps {
  title: string;
  description?: string;
  children: ReactNode;

  className?: string;

  href?: string;

  showViewAll?: boolean;

  variant?: "default" | "featured" | "compact";

  badge?: string;

  icon?: ReactNode;

  loading?: boolean;

  loadingCount?: number;

  onViewAll?: () => void;

  updatedAt?: string;

  algorithm?: string;
}

export function RecommendationSection({
  title,
  description,
  children,

  className,

  href = "#",

  showViewAll = true,

  variant = "default",

  badge,

  icon,

  loading = false,

  loadingCount = 5,

  onViewAll,

  updatedAt = "Updated daily",

  algorithm = "AI Recommendation Engine",
}: RecommendationSectionProps) {
  const sectionId = title.toLowerCase().replace(/\s+/g, "-");

  const resolvedIcon =
    icon ??
    (variant === "featured" ? (
      <Zap className="h-5 w-5" />
    ) : (
      <Sparkles className="h-5 w-5" />
    ));

  const badgeVariant =
    variant === "featured"
      ? "default"
      : variant === "compact"
      ? "secondary"
      : "outline";

  function renderSkeletons() {
    return (
      <div
        className={cn(
          "grid gap-6",
          variant === "compact"
            ? "grid-cols-2 sm:grid-cols-3 lg:grid-cols-4"
            : "grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5"
        )}
      >
        {Array.from({ length: loadingCount }).map((_, index) => (
          <div
            key={index}
            className="overflow-hidden rounded-2xl border bg-card"
          >
            <Skeleton className="aspect-[2/3] w-full rounded-none" />

            <div className="space-y-3 p-4">
              <Skeleton className="h-5 w-4/5" />
              <Skeleton className="h-4 w-3/5" />
              <Skeleton className="h-2 w-full rounded-full" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <section
      aria-labelledby={`${sectionId}-title`}
      aria-describedby={`${sectionId}-description`}
      className={cn(
        variant === "featured"
          ? "space-y-8 rounded-3xl border border-primary/10 bg-gradient-to-br from-primary/5 via-background to-background p-8"
          : "space-y-6",
        className
      )}
    >
      {/* Header */}

      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">

        <div className="flex items-start gap-4">

          <div
            className={cn(
              "flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ring-1 shadow-sm",

              variant === "featured"
                ? "bg-amber-500/10 text-amber-500 ring-amber-500/20"
                : "bg-primary/10 text-primary ring-primary/10"
            )}
          >
            {resolvedIcon}
          </div>

          <div className="space-y-2">

            <div className="flex flex-wrap items-center gap-2">

              <h2
                id={`${sectionId}-title`}
                className={cn(
                  "font-bold tracking-tight",

                  variant === "compact"
                    ? "text-xl"
                    : "text-2xl lg:text-3xl"
                )}
              >
                {title}
              </h2>

              {badge && (
                <Badge
                  variant={badgeVariant}
                  className="rounded-full px-3 py-1 text-[11px]"
                >
                  {badge}
                </Badge>
              )}
            </div>

            {description && (
              <p
                id={`${sectionId}-description`}
                className="max-w-2xl text-sm leading-relaxed text-muted-foreground"
              >
                {description}
              </p>
            )}
          </div>
        </div>

        {/* FIX 1: Header button using buttonVariants */}
        {showViewAll && (
          <Link
            href="/dashboard/recommendations"
            className={cn(
              buttonVariants({
                variant: variant === "featured" ? "default" : "ghost",
                className: "group shrink-0",
              }),
              "flex items-center gap-2"
            )}
          >
            View all recommendations
            <ArrowRight
              className="
                h-4
                w-4
                transition-transform
                duration-300
                group-hover:translate-x-1
              "
            />
          </Link>
        )}
      </div>

      {/* Content */}

      {loading ? renderSkeletons() : children}
            {/* Featured Footer */}

      {variant === "featured" && !loading && (
        <div className="rounded-2xl border border-border/40 bg-muted/20 p-5">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

            <div className="flex flex-wrap items-center gap-5 text-sm text-muted-foreground">

              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-primary" />
                <span>{updatedAt}</span>
              </div>

              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                <span>{algorithm}</span>
              </div>

            </div>

            {/* FIX 2: Featured footer using buttonVariants */}
            {showViewAll && (
              <Link
                href="/dashboard/recommendations"
                className={cn(
                  buttonVariants({
                    variant: "link",
                    className: "p-0 h-auto",
                  }),
                  "group inline-flex items-center gap-2"
                )}
              >
                Explore recommendations
                <ChevronRight
                  className="
                    h-4
                    w-4
                    transition-transform
                    duration-300
                    group-hover:translate-x-1
                  "
                />
              </Link>
            )}
          </div>
        </div>
      )}

      {/* Compact Footer */}

      {variant === "compact" && !loading && showViewAll && (
        <div className="flex justify-end">
          <Link
            href={href}
            className="
              group
              inline-flex
              items-center
              gap-2
              text-sm
              font-medium
              text-primary
              transition-colors
              hover:text-primary/80
            "
          >
            See more

            <ChevronRight
              className="
                h-4
                w-4
                transition-transform
                duration-300
                group-hover:translate-x-1
              "
            />
          </Link>
        </div>
      )}
    </section>
  );
}