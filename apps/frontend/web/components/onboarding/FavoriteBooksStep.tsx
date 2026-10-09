"use client";

import { useEffect, useState } from "react";
import { Check, Loader2 } from "lucide-react";

import { BookCover } from "@/components/books";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface FavoriteBook {
  isbn: string;
  title: string;
  author: string;
  cover_url?: string | null;
  average_rating?: number;
}

interface FavoriteBooksStepProps {
  books: FavoriteBook[];
  loading?: boolean;
  error?: string | null;
  initialSelection?: string[];
  minimumSelection?: number;
  onContinue: (selectedBookIsbns: string[]) => void;
  onRetry?: () => void;
  className?: string;
}

const EMPTY_SELECTION: string[] = [];

export function FavoriteBooksStep({
  books,
  loading = false,
  error = null,
  initialSelection = EMPTY_SELECTION,
  minimumSelection = 5,
  onContinue,
  onRetry,
  className,
}: FavoriteBooksStepProps) {
  const [selected, setSelected] =
    useState<string[]>(initialSelection);

  /*
   * Only synchronize when the parent actually provides
   * a different selection.
   */
  useEffect(() => {
    setSelected(initialSelection);
  }, [initialSelection]);

  function toggleBook(isbn: string) {
    setSelected((previous) => {
      if (previous.includes(isbn)) {
        return previous.filter((item) => item !== isbn);
      }

      return [...previous, isbn];
    });
  }

  if (loading) {
    return (
      <div
        className={cn(
          "flex min-h-[400px] items-center justify-center",
          className
        )}
      >
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />

          <p className="text-sm text-muted-foreground">
            Loading books...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className={cn(
          "flex min-h-[400px] flex-col items-center justify-center text-center",
          className
        )}
      >
        <div className="rounded-3xl border bg-card p-10 shadow-lg">
          <h2 className="text-2xl font-bold">
            Unable to load books
          </h2>

          <p className="mt-2 text-sm text-muted-foreground">
            {error}
          </p>

          {onRetry && (
            <Button
              className="mt-5"
              onClick={onRetry}
            >
              Try Again
            </Button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={cn("space-y-8", className)}>
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold tracking-tight">
          Pick Books You Love
        </h2>

        <p className="mt-3 text-muted-foreground">
          Select at least {minimumSelection} books you&apos;ve
          enjoyed. This helps us understand your reading taste.
        </p>
      </div>

      {/* Books */}
      {books.length === 0 ? (
        <div className="rounded-3xl border bg-card p-10 text-center">
          <p className="text-muted-foreground">
            No books were found.
          </p>

          {onRetry && (
            <Button
              className="mt-5"
              onClick={onRetry}
            >
              Try Again
            </Button>
          )}
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
          {books.map((book) => {
            const active = selected.includes(book.isbn);

            return (
              <button
                key={book.isbn}
                type="button"
                onClick={() => toggleBook(book.isbn)}
                aria-pressed={active}
                className={cn(
                  "group relative rounded-2xl border bg-card p-3 text-left transition-all duration-200",
                  "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
                  active
                    ? "border-primary bg-primary/5 ring-2 ring-primary/20"
                    : "hover:border-primary/30 hover:shadow-md"
                )}
              >
                {/* Selection indicator */}
                {active && (
                  <div className="absolute right-3 top-3 z-30 flex h-7 w-7 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-md">
                    <Check className="h-4 w-4" />
                  </div>
                )}

                {/* Book cover */}
                <div className="pointer-events-none">
                  <BookCover
                    src={book.cover_url ?? undefined}
                    alt={book.title}
                    width={180}
                    height={260}
                    priority={false}
                  />
                </div>

                {/* Book information */}
                <div className="mt-4">
                  <h3 className="line-clamp-2 font-semibold">
                    {book.title}
                  </h3>

                  <p className="mt-1 line-clamp-1 text-sm text-muted-foreground">
                    {book.author}
                  </p>

                  {book.average_rating !== undefined && (
                    <p className="mt-2 text-xs font-medium text-primary">
                      ★ {book.average_rating.toFixed(1)}
                    </p>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      )}

      {/* Bottom controls */}
      <div className="flex items-center justify-between border-t pt-6">
        <div>
          <p className="text-sm font-medium">
            {selected.length} selected
          </p>

          {selected.length < minimumSelection && (
            <p className="mt-1 text-xs text-muted-foreground">
              Select {minimumSelection - selected.length} more
              {minimumSelection - selected.length === 1
                ? " book"
                : " books"}
              .
            </p>
          )}
        </div>

        <Button
          disabled={selected.length < minimumSelection}
          onClick={() => onContinue(selected)}
        >
          Continue
        </Button>
      </div>
    </div>
  );
}

export type { FavoriteBooksStepProps };