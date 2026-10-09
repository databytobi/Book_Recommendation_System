"use client";

import { BookSkeleton } from "@/components/books";
import { cn } from "@/lib/utils";
// FIX: Removed unused 'Search' import
import { Loader2, Sparkles } from "lucide-react";

interface SearchLoadingProps {
  count?: number;
  className?: string;
  variant?: "grid" | "list" | "compact" | "minimal";
  showHeader?: boolean;
  showSearchIndicator?: boolean;
  animationDelay?: number;
}

export function SearchLoading({
  count = 8,
  className,
  variant = "grid",
  showHeader = true,
  showSearchIndicator = true,
  animationDelay = 100,
}: SearchLoadingProps) {
  const isList = variant === "list";
  const isCompact = variant === "compact";
  const isMinimal = variant === "minimal";

  const gridCols = {
    grid: "grid-cols-2 sm:grid-cols-3 lg:grid-cols-4",
    list: "grid-cols-1",
    compact: "grid-cols-2 sm:grid-cols-3",
    minimal: "grid-cols-2 sm:grid-cols-3 lg:grid-cols-4",
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      {showHeader && (
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <div className="h-6 w-32 animate-pulse rounded-md bg-muted" />
              <div className="h-5 w-12 animate-pulse rounded-full bg-muted" />
            </div>
            <div className="h-4 w-48 animate-pulse rounded-md bg-muted" />
          </div>
          {showSearchIndicator && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="hidden sm:inline">Searching...</span>
            </div>
          )}
        </div>
      )}

      {/* Search indicator for minimal variant */}
      {isMinimal && showSearchIndicator && (
        <div className="flex items-center justify-center gap-2 rounded-lg border border-dashed bg-muted/30 py-8">
          <Loader2 className="h-5 w-5 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Searching for books...</p>
        </div>
      )}

      {/* Results count placeholder */}
      {!isMinimal && (
        <div className="flex items-center gap-2">
          <div className="h-4 w-24 animate-pulse rounded bg-muted" />
          <div className="h-4 w-12 animate-pulse rounded bg-muted" />
          <div className="ml-auto h-4 w-16 animate-pulse rounded bg-muted" />
        </div>
      )}

      {/* Grid/List Layout */}
      <div
        className={cn(
          "grid gap-4",
          isList ? "gap-3" : "gap-4 sm:gap-6",
          gridCols[variant],
          className
        )}
      >
        {Array.from({ length: count }).map((_, index) => {
          // Stagger animation delay
          const delay = index * animationDelay;

          if (isList) {
            return (
              <div
                key={index}
                className="animate-fade-in rounded-xl border bg-card p-4"
                style={{ animationDelay: `${delay}ms` }}
              >
                <div className="flex gap-4">
                  <div className="shrink-0">
                    <div className="h-28 w-20 animate-pulse rounded-lg bg-muted" />
                  </div>
                  <div className="flex-1 space-y-3">
                    <div className="space-y-2">
                      <div className="h-5 w-3/4 animate-pulse rounded bg-muted" />
                      <div className="h-4 w-1/2 animate-pulse rounded bg-muted" />
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="h-4 w-24 animate-pulse rounded bg-muted" />
                      <div className="h-4 w-12 animate-pulse rounded bg-muted" />
                    </div>
                    <div className="flex gap-1">
                      <div className="h-6 w-16 animate-pulse rounded-full bg-muted" />
                      <div className="h-6 w-12 animate-pulse rounded-full bg-muted" />
                    </div>
                  </div>
                </div>
              </div>
            );
          }

          if (isCompact) {
            return (
              <div
                key={index}
                className="animate-fade-in rounded-xl border bg-card p-3"
                style={{ animationDelay: `${delay}ms` }}
              >
                <div className="space-y-3">
                  <div className="aspect-[2/3] w-full animate-pulse rounded-lg bg-muted" />
                  <div className="space-y-2">
                    <div className="h-4 w-3/4 animate-pulse rounded bg-muted" />
                    <div className="h-3 w-1/2 animate-pulse rounded bg-muted" />
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-16 animate-pulse rounded bg-muted" />
                      <div className="h-3 w-8 animate-pulse rounded bg-muted" />
                    </div>
                  </div>
                </div>
              </div>
            );
          }

          // Default grid or minimal
          return (
            <div
              key={index}
              className={cn(
                "animate-fade-in",
                !isMinimal && "rounded-xl border bg-card p-4 shadow-sm transition-all"
              )}
              style={{ animationDelay: `${delay}ms` }}
            >
              <BookSkeleton />
              
              {/* Additional shimmer effect for default variant */}
              {!isMinimal && index % 2 === 0 && (
                <div className="absolute inset-0 -z-10 bg-gradient-to-r from-transparent via-primary/5 to-transparent animate-shimmer" />
              )}
            </div>
          );
        })}
      </div>

      {/* Loading footer for default variant */}
      {!isMinimal && !isCompact && (
        <div className="flex items-center justify-center gap-2 pt-2">
          <div className="h-px flex-1 bg-gradient-to-r from-transparent to-muted" />
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground/50">
            <Sparkles className="h-3 w-3" />
            <span>Loading results</span>
          </div>
          <div className="h-px flex-1 bg-gradient-to-l from-transparent to-muted" />
        </div>
      )}
    </div>
  );
}