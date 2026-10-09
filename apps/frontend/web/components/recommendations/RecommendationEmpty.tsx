// apps/frontend/web/components/recommendations/RecommendationEmpty.tsx

"use client";

import Link from "next/link";
import { useState } from "react";
import type { LucideIcon } from "lucide-react";
import {
  BookOpen,
  Sparkles,
  ArrowRight,
  Star,
  Bookmark,
  Library,
  RefreshCw,
  Search,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

// ==========================================================
// TYPES
// ==========================================================

interface SuggestionItem {
  icon: LucideIcon;
  label: string;
  color?: string;
}

interface RecommendationEmptyProps {
  title?: string;
  description?: string;

  actionLabel?: string;
  actionHref?: string;

  secondaryActionLabel?: string;
  secondaryActionHref?: string;

  icon?: React.ReactNode;

  variant?: "default" | "compact" | "minimal";

  recommendationType?:
    | "personalized"
    | "similar"
    | "favorites"
    | "genre"
    | "trending";

  suggestions?: SuggestionItem[];

  showSuggestions?: boolean;

  className?: string;

  onRefresh?: () => void;
}

// ==========================================================
// DEFAULT SUGGESTIONS
// ==========================================================

const DEFAULT_SUGGESTIONS: SuggestionItem[] = [
  {
    icon: Star,
    label: "Rate books you've read",
    color: "text-amber-500",
  },
  {
    icon: Bookmark,
    label: "Save books to your library",
    color: "text-blue-500",
  },
  {
    icon: Search,
    label: "Explore new genres",
    color: "text-emerald-500",
  },
  {
    icon: RefreshCw,
    label: "Refresh recommendations",
    color: "text-violet-500",
  },
];

// ==========================================================
// BADGE LABELS
// ==========================================================

const BADGE_LABELS = {
  personalized: "Personalized",
  similar: "Similar Books",
  favorites: "Favorites",
  genre: "Genre Picks",
  trending: "Trending",
};

// ==========================================================
// COMPONENT
// ==========================================================

export function RecommendationEmpty({
  title = "No recommendations yet",

  description =
    "Start rating books or exploring your library so we can personalize recommendations just for you.",

  actionLabel = "Discover Books",

  actionHref = "/books",

  secondaryActionLabel,

  secondaryActionHref,

  icon,

  variant = "default",

  recommendationType = "personalized",

  suggestions = DEFAULT_SUGGESTIONS,

  showSuggestions = true,

  className,

  onRefresh,
}: RecommendationEmptyProps) {
  const [isHovered, setIsHovered] = useState(false);

  // ========================================================
  // COMPACT
  // ========================================================

  if (variant === "compact") {
    return (
      <div
        className={cn(
          "flex flex-col items-center justify-center rounded-xl border border-dashed bg-card/50 p-8 text-center",
          className
        )}
      >
        <div className="mb-4 rounded-full bg-primary/10 p-3">
          {icon ?? <BookOpen className="h-6 w-6 text-primary" />}
        </div>

        <h4 className="text-base font-semibold">
          {title}
        </h4>

        <p className="mt-2 max-w-sm text-sm text-muted-foreground">
          {description}
        </p>

        <Link href={actionHref}>
          <Button size="sm" className="mt-5 gap-2">
            {actionLabel}
            <ArrowRight className="h-4 w-4" />
          </Button>
        </Link>
      </div>
    );
  }

  // ========================================================
  // MINIMAL
  // ========================================================

  if (variant === "minimal") {
    return (
      <div
        className={cn(
          "flex flex-col items-center justify-center py-12 text-center",
          className
        )}
      >
        <div className="mb-4 rounded-full bg-muted/50 p-4">
          {icon ?? (
            <Sparkles className="h-8 w-8 text-muted-foreground/60" />
          )}
        </div>

        <h4 className="text-lg font-semibold">
          {title}
        </h4>

        <p className="mt-2 text-sm text-muted-foreground">
          {description}
        </p>

        <Link
          href={actionHref}
          className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
        >
          {actionLabel}
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    );
  }

  // ========================================================
  // DEFAULT VARIANT
  // ========================================================

  return (
        <div
      role="status"
      aria-live="polite"
      className={cn(
        "group relative overflow-hidden rounded-2xl border border-dashed bg-card px-8 py-16 text-center transition-all duration-300 hover:shadow-md",
        className
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Background Glow */}
      <div className="absolute -right-24 -top-24 h-64 w-64 rounded-full bg-primary/5 blur-3xl" />
      <div className="absolute -bottom-24 -left-24 h-64 w-64 rounded-full bg-primary/5 blur-3xl" />

      <div className="relative z-10">

        {/* Illustration */}

        <div className="relative mx-auto mb-8 flex h-28 w-28 items-center justify-center">

          <div className="absolute rounded-full bg-primary/10 p-6 transition-all duration-500 group-hover:scale-110">

            {icon ?? (
              <BookOpen className="h-10 w-10 text-primary transition-transform duration-500 group-hover:rotate-3" />
            )}

          </div>

          <Sparkles className="absolute right-1 top-1 h-5 w-5 text-yellow-500" />

          <Library className="absolute bottom-1 left-1 h-5 w-5 text-primary/70" />

        </div>

        {/* Badge */}

        <Badge
          variant="outline"
          className="mb-5"
        >
          <Sparkles className="mr-1 h-3 w-3" />
          {BADGE_LABELS[recommendationType]}
        </Badge>

        {/* Title */}

        <h3 className="text-2xl font-bold tracking-tight">
          {title}
        </h3>

        {/* Description */}

        <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-muted-foreground">
          {description}
        </p>

        {/* Suggestions */}

        {showSuggestions && (
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            {suggestions.map((item, index) => {
              const Icon = item.icon;

              return (
                <div
                  key={index}
                  className="flex items-center gap-2 rounded-full bg-muted/40 px-4 py-2 text-xs text-muted-foreground"
                >
                  <Icon
                    className={cn(
                      "h-3.5 w-3.5",
                      item.color
                    )}
                  />

                  <span>{item.label}</span>
                </div>
              );
            })}
          </div>
        )}

        {/* Actions */}

        <div className="mt-10 flex flex-wrap justify-center gap-3">

          <Link href={actionHref}>
            <Button className="gap-2">
              {actionLabel}

              <ArrowRight
                className={cn(
                  "h-4 w-4 transition-transform duration-300",
                  isHovered && "translate-x-1"
                )}
              />
            </Button>
          </Link>

          {secondaryActionLabel &&
            secondaryActionHref && (
              <Link href={secondaryActionHref}>
                <Button variant="outline">
                  {secondaryActionLabel}
                </Button>
              </Link>
            )}

          {onRefresh && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onRefresh}
              className="rounded-full"
            >
              <RefreshCw
                className={cn(
                  "h-4 w-4",
                  isHovered && "animate-spin"
                )}
              />
            </Button>
          )}
        </div>

        {/* Dynamic Tip */}

        <div className="mt-8 text-xs text-muted-foreground">

          {recommendationType === "personalized" &&
            "💡 Rate at least five books to unlock better personalized recommendations."}

          {recommendationType === "similar" &&
            "💡 Open more books to discover similar titles."}

          {recommendationType === "favorites" &&
            "💡 Add books to your library to receive favorites-based suggestions."}

          {recommendationType === "genre" &&
            "💡 Explore more genres to improve genre recommendations."}

          {recommendationType === "trending" &&
            "💡 Trending recommendations are updated every day."}

        </div>

      </div>
    </div>
  );
}