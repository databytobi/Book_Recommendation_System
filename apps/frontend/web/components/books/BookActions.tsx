// apps/frontend/web/components/books/BookActions.tsx

"use client";

import { memo, MouseEvent, useCallback } from "react";
import {
  Heart,
  Library,
  Eye,
  MoreHorizontal,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface BookActionsProps {
  isFavorite?: boolean;
  isInLibrary?: boolean;
  disabled?: boolean;
  className?: string;

  onFavorite?: () => void;
  onLibrary?: () => void;
  onView?: () => void;
  onMore?: () => void;
}

export const BookActions = memo(function BookActions({
  isFavorite = false,
  isInLibrary = false,
  disabled = false,
  className,
  onFavorite,
  onLibrary,
  onView,
  onMore,
}: BookActionsProps) {

  const stopEvent = (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleFavorite = useCallback(
    (e: MouseEvent<HTMLButtonElement>) => {
      stopEvent(e);
      onFavorite?.();
    },
    [onFavorite]
  );

  const handleLibrary = useCallback(
    (e: MouseEvent<HTMLButtonElement>) => {
      stopEvent(e);
      onLibrary?.();
    },
    [onLibrary]
  );

  const handleView = useCallback(
    (e: MouseEvent<HTMLButtonElement>) => {
      stopEvent(e);
      onView?.();
    },
    [onView]
  );

  const handleMore = useCallback(
    (e: MouseEvent<HTMLButtonElement>) => {
      stopEvent(e);
      onMore?.();
    },
    [onMore]
  );

  return (
    <div
      className={cn(
        "flex items-center justify-between gap-1",
        className
      )}
    >
      {onFavorite && (
        <Button
          size="icon"
          variant="ghost"
          disabled={disabled}
          onClick={handleFavorite}
          aria-label={
            isFavorite
              ? "Remove from favorites"
              : "Add to favorites"
          }
          className={cn(
            "transition-all duration-200 hover:scale-110",
            isFavorite &&
              "bg-red-50 text-red-500 hover:bg-red-100 dark:bg-red-950/20"
          )}
        >
          <Heart
            className={cn(
              "h-4 w-4 transition-colors",
              isFavorite && "fill-current"
            )}
          />
        </Button>
      )}

      {onLibrary && (
        <Button
          size="icon"
          variant="ghost"
          disabled={disabled}
          onClick={handleLibrary}
          aria-label={
            isInLibrary
              ? "Remove from library"
              : "Add to library"
          }
          className={cn(
            "transition-all duration-200 hover:scale-110",
            isInLibrary &&
              "bg-primary/10 text-primary hover:bg-primary/20"
          )}
        >
          <Library
            className={cn(
              "h-4 w-4 transition-colors",
              isInLibrary && "fill-current"
            )}
          />
        </Button>
      )}

      {onView && (
        <Button
          size="icon"
          variant="ghost"
          disabled={disabled}
          onClick={handleView}
          aria-label="View book details"
          className="transition-all duration-200 hover:scale-110"
        >
          <Eye className="h-4 w-4" />
        </Button>
      )}

      {onMore && (
        <Button
          size="icon"
          variant="ghost"
          disabled={disabled}
          onClick={handleMore}
          aria-label="More actions"
          className="transition-all duration-200 hover:scale-110"
        >
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
});

BookActions.displayName = "BookActions";