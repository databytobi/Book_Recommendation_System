"use client";

import {
  SearchX,
  // FIX: Removed unused 'BookOpen'
  Lightbulb,
  RefreshCw,
  Sparkles,
  ArrowRight,
  Library,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface SearchEmptyProps {
  query?: string;
  className?: string;
  onClear?: () => void;
  onSearch?: (query: string) => void;
  title?: string;
  description?: string;
  suggestions?: string[];
  variant?: "default" | "compact" | "minimal";
  showSuggestions?: boolean;
  showActions?: boolean;
}

export function SearchEmpty({
  query,
  className,
  onClear,
  onSearch,
  title = "No books found",
  description,
  suggestions = [
    "Check the spelling",
    "Search by author name",
    "Use fewer keywords",
    "Search with an ISBN",
  ],
  variant = "default",
  showSuggestions = true,
  showActions = true,
}: SearchEmptyProps) {
  const isCompact = variant === "compact";
  const isMinimal = variant === "minimal";

  const defaultDescription = query
    ? `We couldn't find any books matching "${query}"`
    : "Try searching for a book title, author, or ISBN";

  const handleSuggestionClick = (suggestion: string) => {
    if (onSearch) {
      onSearch(suggestion);
    }
  };

  return (
    <div
      className={cn(
        "relative flex flex-col items-center justify-center text-center",
        !isMinimal && "rounded-2xl border border-dashed bg-card/50 px-8 py-16",
        isCompact && "px-4 py-8",
        isMinimal && "border-0 bg-transparent p-0",
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

      {/* Icon */}
      <div
        className={cn(
          "relative flex items-center justify-center rounded-full bg-gradient-to-br from-primary/10 to-primary/5 transition-all duration-300",
          isCompact ? "h-16 w-16" : "h-24 w-24",
          isMinimal && "h-12 w-12"
        )}
      >
        <SearchX
          className={cn(
            "text-muted-foreground/70 transition-all",
            isCompact ? "h-8 w-8" : "h-10 w-10",
            isMinimal && "h-6 w-6"
          )}
        />

        {/* Decorative ring pulse */}
        {!isMinimal && (
          <div className="absolute -inset-1 rounded-full bg-primary/5 blur-md" />
        )}
      </div>

      {/* Content */}
      <div className={cn(
        "space-y-4",
        isCompact ? "mt-4" : "mt-6",
        isMinimal && "mt-3"
      )}>
        {/* Title */}
        <h2 className={cn(
          "font-bold tracking-tight",
          isCompact ? "text-xl" : "text-2xl",
          isMinimal && "text-lg"
        )}>
          {title}
        </h2>

        {/* Description */}
        <p className={cn(
          "mx-auto max-w-md text-muted-foreground",
          isCompact ? "text-sm leading-relaxed" : "text-sm leading-6",
          isMinimal && "text-xs"
        )}>
          {description || defaultDescription}
          {query && (
            <span className="block mt-1 font-medium text-foreground">
              &quot;{query}&quot;
            </span>
          )}
        </p>

        {/* Suggestions */}
        {showSuggestions && (
          <div className="mt-4 space-y-3">
            <div className="flex items-center justify-center gap-2">
              <Lightbulb className="h-4 w-4 text-yellow-500" />
              <p className="text-sm font-medium text-muted-foreground">
                Try these suggestions:
              </p>
            </div>

            <div className="flex flex-wrap justify-center gap-2">
              {suggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className={cn(
                    "inline-flex items-center gap-1.5 rounded-full border border-border/50 bg-card px-4 py-2 text-sm transition-all hover:border-primary/50 hover:bg-primary hover:text-primary-foreground hover:shadow-lg hover:shadow-primary/20",
                    isCompact && "px-3 py-1.5 text-xs",
                    isMinimal && "border-0 bg-transparent px-2 py-1 hover:bg-primary/10 hover:text-primary"
                  )}
                >
                  <span>{suggestion}</span>
                  <ArrowRight className="h-3 w-3 opacity-0 transition-all group-hover:opacity-100" />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        {showActions && (
          <div className="mt-6 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
            {/* Clear Search Button */}
            {onClear && (
              <Button
                variant="outline"
                onClick={onClear}
                className="group gap-2 transition-all hover:gap-3"
                size={isCompact ? "sm" : "default"}
              >
                <RefreshCw className="h-4 w-4 transition-transform group-hover:rotate-180" />
                <span>Clear Search</span>
              </Button>
            )}

            {/* Browse Books Button */}
            <Button
              variant={onClear ? "default" : "outline"}
              onClick={() => window.location.href = "/books"}
              className="group gap-2 transition-all hover:gap-3"
              size={isCompact ? "sm" : "default"}
            >
              <Library className="h-4 w-4" />
              <span>Browse All Books</span>
            </Button>
          </div>
        )}
      </div>

      {/* Decorative footer for default variant */}
      {!isMinimal && !isCompact && (
        <div className="mt-8 flex items-center gap-2">
          <div className="h-px flex-1 bg-gradient-to-r from-primary/10 to-transparent" />
          <div className="flex items-center gap-1 text-[10px] text-muted-foreground/50">
            <Sparkles className="h-3 w-3" />
            <span>Keep searching</span>
          </div>
          <div className="h-px flex-1 bg-gradient-to-l from-primary/10 to-transparent" />
        </div>
      )}
    </div>
  );
}