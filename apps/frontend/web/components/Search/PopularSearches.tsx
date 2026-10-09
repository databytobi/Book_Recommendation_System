"use client";

import { useState } from "react";
import {
  TrendingUp,
  Flame,
  // FIX: Removed unused 'Clock'
  ChevronRight,
  // FIX: Removed unused 'Sparkles'
  Search,
  ArrowRight,
  // FIX: Removed unused 'X'
  Zap,
} from "lucide-react";

// FIX: Removed unused 'Badge' import
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface PopularSearch {
  id: string | number;
  label: string;
  searchCount?: number;
  trend?: number; // Percentage change
  category?: string;
  isHot?: boolean;
  isNew?: boolean;
}

interface PopularSearchesProps {
  searches: PopularSearch[];
  className?: string;
  onSelect: (query: string) => void;
  title?: string;
  subtitle?: string;
  maxDisplay?: number;
  variant?: "default" | "compact" | "minimal";
  showCounts?: boolean;
  showTrends?: boolean;
  onViewAll?: () => void;
}

function TrendIndicator({ trend }: { trend?: number }) {
  if (!trend) return null;
  
  const isPositive = trend > 0;
  const isNegative = trend < 0;
  
  return (
    <span
      className={cn(
        "inline-flex items-center gap-0.5 text-[10px] font-medium",
        isPositive && "text-emerald-500",
        isNegative && "text-red-500",
        !isPositive && !isNegative && "text-muted-foreground"
      )}
    >
      {isPositive && "↑"}
      {isNegative && "↓"}
      {trend !== 0 && Math.abs(trend)}%
    </span>
  );
}

function SearchTag({
  search,
  variant,
  showCounts,
  showTrends,
  onSelect,
}: {
  search: PopularSearch;
  variant?: "default" | "compact" | "minimal";
  showCounts?: boolean;
  showTrends?: boolean;
  onSelect: (query: string) => void;
}) {
  const [isHovered, setIsHovered] = useState(false);
  const isCompact = variant === "compact";
  const isMinimal = variant === "minimal";

  return (
    <button
      key={search.id}
      className={cn(
        "group relative inline-flex items-center gap-2 transition-all duration-300",
        "focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2",
        isMinimal 
          ? "px-3 py-1.5 text-sm hover:text-primary"
          : cn(
              "rounded-full border border-border/50 bg-card px-4 py-2 text-sm",
              "hover:border-primary/50 hover:bg-primary hover:text-primary-foreground",
              "hover:shadow-lg hover:shadow-primary/20",
              isCompact && "px-3 py-1.5 text-xs"
            )
      )}
      onClick={() => onSelect(search.label)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Hot/New badge */}
      {search.isHot && !isMinimal && (
        <span className="absolute -right-1 -top-1 flex h-3 w-3">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-400 opacity-75" />
          <span className="relative inline-flex h-3 w-3 rounded-full bg-red-500" />
        </span>
      )}
      
      {search.isNew && !isMinimal && (
        <span className="absolute -right-1 -top-1 rounded-full bg-blue-500 px-1.5 py-0.5 text-[8px] font-bold text-white">
          NEW
        </span>
      )}

      {/* Search icon for minimal variant */}
      {isMinimal && (
        <Search className="h-3.5 w-3.5 text-muted-foreground transition-colors group-hover:text-primary" />
      )}

      {/* Label */}
      <span className={cn(
        "font-medium transition-colors",
        isMinimal && "group-hover:text-primary"
      )}>
        {search.label}
      </span>

      {/* Category */}
      {search.category && !isMinimal && (
        <span className="text-[10px] text-muted-foreground/70 group-hover:text-primary-foreground/70">
          {search.category}
        </span>
      )}

      {/* Search count */}
      {showCounts && search.searchCount !== undefined && !isMinimal && (
        <span className={cn(
          "text-xs transition-colors",
          isHovered 
            ? "text-primary-foreground/90" 
            : "text-muted-foreground"
        )}>
          {search.searchCount >= 1000 
            ? `${(search.searchCount / 1000).toFixed(1)}K` 
            : search.searchCount.toLocaleString()}
        </span>
      )}

      {/* Trend indicator */}
      {showTrends && search.trend !== undefined && !isMinimal && (
        <TrendIndicator trend={search.trend} />
      )}

      {/* Arrow on hover for default variant */}
      {!isMinimal && (
        <ChevronRight 
          className={cn(
            "h-3.5 w-3.5 transition-all duration-300",
            isHovered 
              ? "translate-x-0.5 text-primary-foreground" 
              : "opacity-0 -translate-x-2"
          )}
        />
      )}

      {/* Pop effect on hover */}
      {!isMinimal && isHovered && (
        <span className="absolute inset-0 -z-10 rounded-full bg-primary/10 blur-xl transition-all duration-500" />
      )}
    </button>
  );
}

export function PopularSearches({
  searches,
  className,
  onSelect,
  title = "Trending Searches",
  subtitle = "Discover what readers are exploring right now",
  maxDisplay = 8,
  variant = "default",
  showCounts = true,
  showTrends = false,
  onViewAll,
}: PopularSearchesProps) {
  const [showAll, setShowAll] = useState(false);
  const isCompact = variant === "compact";
  const isMinimal = variant === "minimal";

  if (searches.length === 0) {
    return null;
  }

  const displaySearches = showAll ? searches : searches.slice(0, maxDisplay);
  const hasMore = searches.length > maxDisplay;

  return (
    <section
      className={cn(
        "space-y-4",
        !isMinimal && "rounded-2xl border bg-card p-6 transition-all hover:shadow-lg hover:shadow-primary/5",
        isCompact && "p-4",
        isMinimal && "border-0 bg-transparent p-0 shadow-none",
        className
      )}
    >
      {/* Decorative background for default variant */}
      {!isMinimal && (
        <div className="absolute inset-0 -z-10 overflow-hidden rounded-2xl">
          <div className="absolute -right-20 -top-20 h-40 w-40 rounded-full bg-primary/5 blur-2xl" />
          <div className="absolute -bottom-20 -left-20 h-40 w-40 rounded-full bg-secondary/5 blur-2xl" />
        </div>
      )}

      {/* Header */}
      <div className={cn(
        "flex items-start justify-between gap-4",
        isCompact && "flex-col sm:flex-row sm:items-center"
      )}>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            {isMinimal ? (
              <Flame className="h-4 w-4 text-orange-500" />
            ) : (
              <div className="rounded-lg bg-gradient-to-br from-orange-500/10 to-yellow-500/10 p-1.5">
                <TrendingUp className="h-4 w-4 text-orange-500" />
              </div>
            )}
            <h3 className={cn(
              "font-bold tracking-tight",
              isCompact ? "text-base" : "text-lg"
            )}>
              {title}
            </h3>
            {!isMinimal && searches.length > 0 && (
              <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                {searches.length}
              </span>
            )}
          </div>
          {subtitle && !isCompact && !isMinimal && (
            <p className="text-sm text-muted-foreground">
              {subtitle}
            </p>
          )}
        </div>

        {onViewAll && !isMinimal && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onViewAll}
            className="group shrink-0 gap-1 transition-all hover:gap-2"
          >
            <span>View All</span>
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </Button>
        )}
      </div>

      {/* Search Tags */}
      <div className={cn(
        "flex flex-wrap gap-2",
        isMinimal && "gap-1.5",
        isCompact && "gap-1.5"
      )}>
        {displaySearches.map((search) => (
          <SearchTag
            key={search.id}
            search={search}
            variant={variant}
            showCounts={showCounts}
            showTrends={showTrends}
            onSelect={onSelect}
          />
        ))}
      </div>

      {/* Show All / Show Less */}
      {hasMore && !isMinimal && (
        <div className="flex justify-center pt-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowAll(!showAll)}
            className="group gap-1 text-muted-foreground transition-all hover:gap-2 hover:text-primary"
          >
            <span>
              {showAll ? "Show Less" : `Show ${searches.length - maxDisplay} More`}
            </span>
            <ChevronRight
              className={cn(
                "h-4 w-4 transition-transform",
                showAll && "rotate-180"
              )}
            />
          </Button>
        </div>
      )}

      {/* Decorative footer for default variant */}
      {!isMinimal && searches.length > 0 && (
        <div className="flex items-center gap-2 pt-2">
          <div className="h-px flex-1 bg-gradient-to-r from-primary/10 to-transparent" />
          <div className="flex items-center gap-1 text-[10px] text-muted-foreground/50">
            <Zap className="h-3 w-3" />
            <span>Live trends</span>
          </div>
          <div className="h-px flex-1 bg-gradient-to-l from-primary/10 to-transparent" />
        </div>
      )}
    </section>
  );
}