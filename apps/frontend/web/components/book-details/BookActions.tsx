"use client";

import {
  BookOpen,
  Bookmark,
  Heart,
  Share2,
  CheckCircle2,
  Sparkles,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface BookActionsProps {
  className?: string;
  isSaved?: boolean;
  isFavorite?: boolean;
  isCompleted?: boolean;
  isReading?: boolean;
  onRead?: () => void;
  onSave?: () => void;
  onFavorite?: () => void;
  onComplete?: () => void;
  onShare?: () => void;
  showLabels?: boolean;
  size?: "default" | "sm" | "lg";
}

export function BookActions({
  className,
  isSaved = false,
  isFavorite = false,
  isCompleted = false,
  isReading = false,
  onRead,
  onSave,
  onFavorite,
  onComplete,
  onShare,
  showLabels = true,
  size = "default",
}: BookActionsProps) {
  const buttonSize = size === "sm" ? "sm" : size === "lg" ? "lg" : "default";
  const iconSize = size === "sm" ? "h-3.5 w-3.5" : "h-4 w-4";

  return (
    <div
      className={cn(
        "flex flex-wrap items-center gap-3",
        className
      )}
    >
      {/* Primary Read Button */}
      <Button
        size={buttonSize}
        onClick={onRead}
        className={cn(
          "group relative min-w-[120px] transition-all hover:scale-[1.02] hover:shadow-lg hover:shadow-primary/20",
          isReading && "bg-primary/90"
        )}
      >
        <BookOpen className={cn("mr-2", iconSize, "transition-transform group-hover:scale-110")} />
        <span className="transition-all">
          {isReading ? "Continue Reading" : "Read Now"}
        </span>
        {isReading && (
          <span className="absolute -right-1 -top-1">
            <span className="flex h-3 w-3">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary/60 opacity-75" />
              <span className="relative inline-flex h-3 w-3 rounded-full bg-primary" />
            </span>
          </span>
        )}
      </Button>

      {/* Action Buttons Group */}
      <div className="flex flex-wrap gap-2">
        {/* Save Button */}
        <Button
          variant={isSaved ? "default" : "outline"}
          size={buttonSize}
          onClick={onSave}
          className={cn(
            "group transition-all hover:scale-105",
            isSaved && "bg-emerald-500 hover:bg-emerald-600"
          )}
        >
          <Bookmark
            className={cn(
              iconSize,
              "transition-all",
              isSaved && "fill-current",
              !isSaved && "group-hover:fill-primary/20"
            )}
          />
          {showLabels && (
            <span className="ml-2">
              {isSaved ? "Saved" : "Save"}
            </span>
          )}
        </Button>

        {/* Favorite Button */}
        <Button
          variant={isFavorite ? "default" : "outline"}
          size={buttonSize}
          onClick={onFavorite}
          className={cn(
            "group transition-all hover:scale-105",
            isFavorite && "bg-rose-500 hover:bg-rose-600"
          )}
        >
          <Heart
            className={cn(
              iconSize,
              "transition-all",
              isFavorite && "fill-current",
              !isFavorite && "group-hover:fill-rose-500/20"
            )}
          />
          {showLabels && (
            <span className="ml-2">
              {isFavorite ? "Favorited" : "Favorite"}
            </span>
          )}
        </Button>

        {/* Complete Button */}
        <Button
          variant={isCompleted ? "default" : "outline"}
          size={buttonSize}
          onClick={onComplete}
          className={cn(
            "group transition-all hover:scale-105",
            isCompleted && "bg-violet-500 hover:bg-violet-600"
          )}
        >
          <CheckCircle2
            className={cn(
              iconSize,
              "transition-all",
              isCompleted && "fill-current"
            )}
          />
          {showLabels && (
            <span className="ml-2">
              {isCompleted ? "Completed" : "Mark Read"}
            </span>
          )}
        </Button>
      </div>

      {/* Share Button */}
      <Button
        variant="outline"
        size={buttonSize === "lg" ? "lg" : "default"}
        onClick={onShare}
        className="group transition-all hover:scale-105 hover:border-primary/50 hover:bg-primary/5"
      >
        <Share2 className={cn(iconSize, "transition-transform group-hover:rotate-12")} />
        {showLabels && size !== "sm" && (
          <span className="ml-2 hidden sm:inline">Share</span>
        )}
      </Button>

      {/* Optional: Reading Progress Indicator */}
      {isReading && (
        <div className="ml-2 flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
          <Sparkles className="h-3 w-3" />
          <span>Reading</span>
        </div>
      )}
    </div>
  );
}