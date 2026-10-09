"use client";

import { useState, useRef } from "react"; // FIX: Removed unused 'useEffect'
import { ChevronDown, ChevronUp, BookOpen, Quote } from "lucide-react";

import { cn } from "@/lib/utils";

interface BookDescriptionProps {
  description: string;
  className?: string;
  truncateLength?: number;
  showHeader?: boolean;
  variant?: "default" | "compact" | "minimal";
  title?: string;
}

export function BookDescription({
  description,
  className,
  truncateLength = 350,
  showHeader = true,
  variant = "default",
  title = "About this book",
}: BookDescriptionProps) {
  const [expanded, setExpanded] = useState(false);
  // FIX: Removed isOverflowing state
  const contentRef = useRef<HTMLParagraphElement>(null);

  const shouldTruncate = description.length > truncateLength;

  // FIX: Removed useEffect that checked isOverflowing

  const displayedText = !shouldTruncate || expanded
    ? description
    : `${description.slice(0, truncateLength)}...`;

  const isCompact = variant === "compact";
  const isMinimal = variant === "minimal";

  return (
    <section
      className={cn(
        "group relative rounded-2xl border bg-card p-6 transition-all hover:shadow-lg hover:shadow-primary/5",
        isCompact && "p-4",
        isMinimal && "border-0 bg-transparent p-0 shadow-none hover:shadow-none",
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
      {showHeader && !isMinimal && (
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-primary/10 p-2 text-primary">
              <BookOpen className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
              <p className="text-sm text-muted-foreground">
                What readers need to know
              </p>
            </div>
          </div>
          {isCompact && shouldTruncate && (
            <button
              type="button"
              onClick={() => setExpanded((prev) => !prev)}
              className="inline-flex items-center gap-1 text-sm font-medium text-primary transition-all hover:gap-2"
            >
              {expanded ? (
                <>
                  <span>Less</span>
                  <ChevronUp className="h-4 w-4" />
                </>
              ) : (
                <>
                  <span>More</span>
                  <ChevronDown className="h-4 w-4" />
                </>
              )}
            </button>
          )}
        </div>
      )}

      {/* Description Content */}
      <div
        className={cn(
          "relative",
          showHeader && !isMinimal && "mt-4",
          isMinimal && "mt-0"
        )}
      >
        {/* Quote icon for default variant */}
        {!isMinimal && !isCompact && (
          <Quote className="absolute -left-1 -top-1 h-8 w-8 text-primary/10" />
        )}

        <div
          className={cn(
            "relative",
            !expanded && shouldTruncate && !isMinimal && "overflow-hidden"
          )}
          style={{
            maxHeight: !expanded && shouldTruncate && !isMinimal 
              ? `${isCompact ? 80 : 160}px` 
              : "none"
          }}
        >
          <p
            ref={contentRef}
            className={cn(
              "whitespace-pre-line leading-relaxed text-muted-foreground",
              isCompact && "text-sm",
              isMinimal && "text-base leading-7",
              !isMinimal && "pl-6"
            )}
          >
            {displayedText}
          </p>

          {/* Gradient fade for truncated text */}
          {!expanded && shouldTruncate && !isMinimal && (
            <div
              className={cn(
                "absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-card to-transparent",
                isMinimal && "from-background"
              )}
            />
          )}
        </div>

        {/* Read More/Less button for default and compact variants */}
        {shouldTruncate && !isCompact && !isMinimal && (
          <div className="mt-4 flex items-center gap-4">
            <button
              type="button"
              onClick={() => setExpanded((prev) => !prev)}
              className="group inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2 text-sm font-medium text-primary transition-all hover:bg-primary/20 hover:pl-5"
            >
              {expanded ? (
                <>
                  <span>Show Less</span>
                  <ChevronUp className="h-4 w-4 transition-transform group-hover:-translate-y-0.5" />
                </>
              ) : (
                <>
                  <span>Read More</span>
                  <ChevronDown className="h-4 w-4 transition-transform group-hover:translate-y-0.5" />
                </>
              )}
            </button>

            {/* FIX: Removed reading time estimate with Sparkles */}
          </div>
        )}
      </div>

      {/* Minimal variant button at bottom */}
      {shouldTruncate && isMinimal && (
        <button
          type="button"
          onClick={() => setExpanded((prev) => !prev)}
          className="mt-3 inline-flex items-center gap-2 text-sm font-medium text-primary transition-all hover:gap-3"
        >
          {expanded ? (
            <>
              Show Less
              <ChevronUp className="h-4 w-4" />
            </>
          ) : (
            <>
              Read More
              <ChevronDown className="h-4 w-4" />
            </>
          )}
        </button>
      )}
    </section>
  );
}