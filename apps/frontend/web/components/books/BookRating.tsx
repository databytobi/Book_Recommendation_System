// apps/frontend/web/components/books/BookRating.tsx

"use client";

import { Star, StarHalf } from "lucide-react";
import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
// FIX: Removed unused 'Badge' import

interface BookRatingProps {
  rating: number;
  ratingsCount?: number;
  showValue?: boolean;
  showCount?: boolean;
  showStars?: boolean;
  // FIX 2: Use the actual size type from BookRatingProps
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  variant?: "default" | "primary" | "outline" | "compact" | "minimal";
  maxRating?: number;
  className?: string;
  onRate?: (rating: number) => void;
  interactive?: boolean;
  disabled?: boolean;
  tooltip?: string;
}

const sizeMap = {
  xs: {
    star: "h-3 w-3",
    text: "text-[10px]",
    gap: "gap-1",
  },
  sm: {
    star: "h-3.5 w-3.5",
    text: "text-xs",
    gap: "gap-1.5",
  },
  md: {
    star: "h-4 w-4",
    text: "text-sm",
    gap: "gap-1.5",
  },
  lg: {
    star: "h-5 w-5",
    text: "text-base",
    gap: "gap-2",
  },
  xl: {
    star: "h-6 w-6",
    text: "text-lg",
    gap: "gap-2.5",
  },
};

const variantStyles = {
  default: "text-foreground",
  primary: "text-primary",
  outline: "border border-border/50 rounded-full px-3 py-1 bg-card/50",
  compact: "bg-muted/30 rounded-lg px-2 py-1",
  minimal: "text-muted-foreground",
};

export function BookRating({
  rating,
  ratingsCount,
  showValue = true,
  showCount = true,
  showStars = false,
  size = "md",
  variant = "default",
  maxRating = 5,
  className,
  onRate,
  interactive = false,
  disabled = false,
  tooltip,
}: BookRatingProps) {
  const styles = sizeMap[size];
  const roundedRating = Math.round(rating * 2) / 2;
  const fullStars = Math.floor(roundedRating);
  const hasHalfStar = roundedRating % 1 !== 0;
  const emptyStars = maxRating - Math.ceil(roundedRating);

  // Generate star array
  const renderStars = () => {
    const stars = [];

    // Full stars
    for (let i = 0; i < fullStars; i++) {
      stars.push(
        <Star
          key={`full-${i}`}
          className={cn(
            styles.star,
            "fill-yellow-400 text-yellow-400",
            interactive && "cursor-pointer transition-transform hover:scale-110",
            disabled && "cursor-not-allowed opacity-60"
          )}
          onClick={() => interactive && !disabled && onRate?.(i + 1)}
          // FIX 5: Accessibility
          role="button"
          tabIndex={0}
          aria-label={`Rate ${i + 1} stars`}
        />
      );
    }

    // Half star
    if (hasHalfStar) {
      stars.push(
        <div
          key="half"
          className="relative"
          onClick={() => interactive && !disabled && onRate?.(fullStars + 1)} // FIX 6: Simplified to full star
        >
          <Star
            className={cn(
              styles.star,
              "text-yellow-400/30 fill-yellow-400/30",
              interactive && "cursor-pointer transition-transform hover:scale-110",
              disabled && "cursor-not-allowed opacity-60"
            )}
            role="button"
            tabIndex={0}
            aria-label={`Rate ${fullStars + 1} stars`} // FIX 5: Accessibility
          />
          <StarHalf
            className={cn(
              styles.star,
              "absolute inset-0 fill-yellow-400 text-yellow-400",
              interactive && "cursor-pointer transition-transform hover:scale-110",
              disabled && "cursor-not-allowed opacity-60"
            )}
            role="button"
            tabIndex={0}
            aria-label={`Rate ${fullStars + 1} stars`} // FIX 5: Accessibility
          />
        </div>
      );
    }

    // Empty stars
    for (let i = 0; i < emptyStars; i++) {
      const starIndex = fullStars + (hasHalfStar ? 1 : 0) + i + 1;
      stars.push(
        <Star
          key={`empty-${i}`}
          className={cn(
            styles.star,
            "text-muted-foreground/30",
            interactive && "cursor-pointer transition-transform hover:scale-110 hover:text-yellow-400/50",
            disabled && "cursor-not-allowed opacity-60"
          )}
          onClick={() => interactive && !disabled && onRate?.(starIndex)}
          // FIX 5: Accessibility
          role="button"
          tabIndex={0}
          aria-label={`Rate ${starIndex} stars`}
        />
      );
    }

    return stars;
  };

  // FIX 1: Removed fake rating distribution
  // The entire getRatingDistribution function has been removed

  const ratingContent = (
    <div
      className={cn(
        "flex items-center",
        styles.gap,
        variantStyles[variant],
        className
      )}
    >
      {/* Stars */}
      {showStars && (
        <div className="flex items-center gap-0.5">
          {renderStars()}
        </div>
      )}

      {/* Rating Value */}
      {showValue && (
        <span className={cn("font-semibold", styles.text)}>
          {rating.toFixed(1)}
        </span>
      )}

      {/* FIX 1: Cleaner rating display */}
      {showCount && ratingsCount !== undefined && (
        <span className={cn("text-muted-foreground", styles.text)}>
          ({ratingsCount.toLocaleString()})
        </span>
      )}

      {/* FIX 3: Removed "Click to rate" badge */}
    </div>
  );

  // Wrap with tooltip if provided
  if (tooltip) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger className="cursor-help">
            {ratingContent}
          </TooltipTrigger>
          <TooltipContent side="top" className="max-w-xs">
            <div className="space-y-2">
              <p className="text-sm font-medium">{tooltip}</p>
              {ratingsCount && (
                <p className="text-xs text-muted-foreground">
                  Based on {ratingsCount.toLocaleString()} ratings.
                </p>
              )}
            </div>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return ratingContent;
}

// ============================================================
// Sub-components for specific use cases
// ============================================================

interface BookRatingSimpleProps {
  rating: number;
  ratingsCount?: number;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function BookRatingSimple({
  rating,
  ratingsCount,
  size = "md",
  className,
}: BookRatingSimpleProps) {
  return (
    <BookRating
      rating={rating}
      ratingsCount={ratingsCount}
      size={size}
      className={className}
      showStars={false}
      variant="default"
    />
  );
}

export function BookRatingStars({
  rating,
  size = "md",
  className,
}: {
  rating: number;
  size?: "sm" | "md" | "lg";
  className?: string;
}) {
  return (
    <BookRating
      rating={rating}
      size={size}
      className={className}
      showStars={true}
      showValue={false}
      showCount={false}
      variant="default"
    />
  );
}

export function BookRatingInteractive({
  rating,
  onRate,
  size = "md",
  disabled = false,
}: {
  rating: number;
  onRate: (rating: number) => void;
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
}) {
  return (
    <BookRating
      rating={rating}
      size={size}
      showStars={true}
      showValue={true}
      showCount={false}
      interactive={true}
      disabled={disabled}
      onRate={onRate}
      variant="default"
      // FIX 4: Tooltip now contains useful information
      tooltip={`Rate this book (${rating.toFixed(1)} / 5.0)`}
    />
  );
}