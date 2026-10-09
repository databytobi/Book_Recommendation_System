"use client";

import { useState } from "react";
import {
  Clock3,
  X,
  // FIX: Removed unused 'Search'
  Trash2,
  History,
  // FIX: Removed unused 'Sparkles'
  ArrowRight,
  Clock,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface SearchHistoryProps {
  history: string[];
  className?: string;
  onSelect: (query: string) => void;
  onRemove?: (query: string) => void;
  onClearAll?: () => void;
  title?: string;
  subtitle?: string;
  maxDisplay?: number;
  variant?: "default" | "compact" | "minimal";
  showTimestamps?: boolean;
  showCounts?: boolean;
}

interface HistoryItemProps {
  query: string;
  index: number;
  onSelect: (query: string) => void;
  onRemove?: (query: string) => void;
  variant?: "default" | "compact" | "minimal";
  showTimestamp?: boolean;
  timestamp?: string;
}

function HistoryItem({
  query,
  index,
  onSelect,
  onRemove,
  variant = "default",
  showTimestamp = false,
  timestamp = "2 hours ago",
}: HistoryItemProps) {
  const [isHovered, setIsHovered] = useState(false);
  const isCompact = variant === "compact";
  const isMinimal = variant === "minimal";

  return (
    <div
      className={cn(
        "group flex items-center gap-3 transition-all duration-300",
        !isMinimal && cn(
          "rounded-xl border bg-card px-4 py-3",
          "hover:border-primary/30 hover:bg-primary/5 hover:shadow-md hover:shadow-primary/5"
        ),
        isCompact && "px-3 py-2",
        isMinimal && "border-0 bg-transparent px-2 py-2 hover:bg-primary/5"
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Icon */}
      <div
        className={cn(
          "flex shrink-0 items-center justify-center rounded-lg transition-all",
          !isMinimal && "bg-primary/10",
          isCompact ? "h-8 w-8" : "h-9 w-9",
          isMinimal && "h-6 w-6"
        )}
      >
        <Clock3
          className={cn(
            "text-muted-foreground transition-colors group-hover:text-primary",
            isCompact ? "h-3.5 w-3.5" : "h-4 w-4",
            isMinimal && "h-3.5 w-3.5"
          )}
        />
      </div>

      {/* Content */}
      <button
        type="button"
        onClick={() => onSelect(query)}
        className="flex flex-1 items-center gap-2 text-left"
      >
        <div className="flex-1 min-w-0">
          <span className={cn(
            "font-medium transition-colors group-hover:text-primary",
            isCompact ? "text-sm" : "text-sm",
            isMinimal && "text-sm"
          )}>
            {query}
          </span>
          {showTimestamp && timestamp && !isMinimal && (
            <div className="flex items-center gap-1 text-xs text-muted-foreground/70">
              <Clock className="h-3 w-3" />
              <span>{timestamp}</span>
            </div>
          )}
        </div>

        {/* Search count badge */}
        {!isMinimal && (
          <span className="text-xs text-muted-foreground/50">
            #{index + 1}
          </span>
        )}
      </button>

      {/* Actions */}
      <div className="flex shrink-0 items-center gap-1">
        {onRemove && (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => onRemove(query)}
            className={cn(
              "h-8 w-8 transition-all duration-300",
              isHovered ? "opacity-100" : "opacity-0",
              isMinimal && "opacity-100 hover:bg-destructive/10 hover:text-destructive"
            )}
          >
            <X className="h-3.5 w-3.5" />
          </Button>
        )}

        {/* Arrow on hover for default variant */}
        {!isMinimal && (
          <ArrowRight
            className={cn(
              "h-4 w-4 transition-all duration-300",
              isHovered 
                ? "translate-x-0.5 text-primary opacity-100" 
                : "opacity-0 -translate-x-2"
            )}
          />
        )}
      </div>
    </div>
  );
}

export function SearchHistory({
  history,
  className,
  onSelect,
  onRemove,
  onClearAll,
  title = "Recent Searches",
  subtitle = "Your search history",
  maxDisplay = 10,
  variant = "default",
  showTimestamps = false,
  // FIX: Removed unused '_showCounts' entirely
}: SearchHistoryProps) {
  const [showAll, setShowAll] = useState(false);
  const isCompact = variant === "compact";
  const isMinimal = variant === "minimal";

  if (history.length === 0) {
    return null;
  }

  const displayHistory = showAll ? history : history.slice(0, maxDisplay);
  const hasMore = history.length > maxDisplay;

  // Mock timestamps - in real app, this would come from the data
  const mockTimestamps = [
    "Just now",
    "2 hours ago",
    "Yesterday",
    "2 days ago",
    "3 days ago",
    "Last week",
    "2 weeks ago",
  ];

  return (
    <section
      className={cn(
        "relative",
        !isMinimal && "rounded-2xl border bg-card p-5 transition-all hover:shadow-lg hover:shadow-primary/5",
        isCompact && "p-3",
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
            {!isMinimal && (
              <div className="rounded-lg bg-primary/10 p-1.5">
                <History className="h-4 w-4 text-primary" />
              </div>
            )}
            <h3 className={cn(
              "font-bold tracking-tight",
              isCompact ? "text-base" : "text-lg",
              isMinimal && "text-sm"
            )}>
              {title}
            </h3>
            {!isMinimal && history.length > 0 && (
              <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                {history.length}
              </span>
            )}
          </div>
          {subtitle && !isCompact && !isMinimal && (
            <p className="text-sm text-muted-foreground">
              {subtitle}
            </p>
          )}
        </div>

        <div className="flex shrink-0 items-center gap-2">
          {onClearAll && !isMinimal && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onClearAll}
              className="gap-1.5 text-muted-foreground transition-all hover:gap-2 hover:text-destructive"
            >
              <Trash2 className="h-3.5 w-3.5" />
              <span className={cn(isCompact ? "hidden sm:inline" : "inline")}>
                Clear All
              </span>
            </Button>
          )}
        </div>
      </div>

      {/* History List */}
      <div className={cn(
        !isMinimal && "mt-4",
        isCompact && "mt-3"
      )}>
        <div className={cn(
          "space-y-2",
          isCompact && "space-y-1.5"
        )}>
          {displayHistory.map((query, index) => (
            <HistoryItem
              key={`${query}-${index}`}
              query={query}
              index={index}
              onSelect={onSelect}
              onRemove={onRemove}
              variant={variant}
              showTimestamp={showTimestamps}
              timestamp={mockTimestamps[index % mockTimestamps.length]}
            />
          ))}
        </div>

        {/* Show More / Show Less */}
        {hasMore && !isMinimal && (
          <div className="mt-3 flex justify-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAll(!showAll)}
              className="group gap-1 text-muted-foreground transition-all hover:gap-2 hover:text-primary"
            >
              <span>
                {showAll 
                  ? "Show Less" 
                  : `Show ${Math.min(history.length - maxDisplay, 5)} More`}
              </span>
              <ArrowRight
                className={cn(
                  "h-3.5 w-3.5 transition-transform",
                  showAll && "rotate-180"
                )}
              />
            </Button>
          </div>
        )}
      </div>

      {/* Decorative footer for default variant */}
      {!isMinimal && !isCompact && history.length > 0 && (
        <div className="mt-4 flex items-center gap-2">
          <div className="h-px flex-1 bg-gradient-to-r from-primary/10 to-transparent" />
          <div className="flex items-center gap-1 text-[10px] text-muted-foreground/50">
            <Clock className="h-3 w-3" />
            <span>Recent searches</span>
          </div>
          <div className="h-px flex-1 bg-gradient-to-l from-primary/10 to-transparent" />
        </div>
      )}
    </section>
  );
}