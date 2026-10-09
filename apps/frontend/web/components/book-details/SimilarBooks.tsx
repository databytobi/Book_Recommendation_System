"use client";

import { useState } from "react";
import { ChevronRight, BookOpen, Sparkles, ArrowRight } from "lucide-react";

// ✅ Import from the books folder
import { BookCard } from "../books/BookCard";
// OR if you have the index file set up:
// import { BookCard } from "@/components/books";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface SimilarBook {
  id: string | number;
  title: string;
  author: string;
  coverUrl?: string;
  rating?: number;
  publicationYear?: number;
  genre?: string;
  isNew?: boolean;
}

interface SimilarBooksProps {
  books: SimilarBook[];
  className?: string;
  loading?: boolean;
  onBookClick?: (book: SimilarBook) => void;
  onViewAll?: () => void;
  title?: string;
  subtitle?: string;
  maxDisplay?: number;
  variant?: "default" | "compact" | "minimal";
}

function BookSkeleton() {
  return (
    <div className="group rounded-xl border bg-card p-4 transition-all">
      <div className="animate-pulse">
        <div className="aspect-[2/3] w-full rounded-lg bg-muted" />
        <div className="mt-3 h-4 w-3/4 rounded bg-muted" />
        <div className="mt-2 h-3 w-1/2 rounded bg-muted" />
        <div className="mt-3 flex items-center gap-2">
          <div className="h-3 w-16 rounded bg-muted" />
          <div className="h-3 w-8 rounded bg-muted" />
        </div>
      </div>
    </div>
  );
}

export function SimilarBooks({
  books,
  loading = false,
  className,
  onBookClick,
  onViewAll,
  title = "Similar Books",
  subtitle = "Readers who enjoyed this book also liked these.",
  maxDisplay = 4,
  variant = "default",
}: SimilarBooksProps) {
  const [visibleCount, setVisibleCount] = useState(maxDisplay);
  const isCompact = variant === "compact";
  const isMinimal = variant === "minimal";

  const displayBooks = books.slice(0, visibleCount);
  const hasMore = books.length > visibleCount;
  const shouldShowLoadMore = hasMore && !isMinimal;

  return (
    <section
      className={cn(
        "relative",
        !isMinimal && "rounded-2xl border bg-card p-6 transition-all hover:shadow-lg hover:shadow-primary/5",
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
      <div className={cn(
        "flex items-start justify-between gap-4",
        isCompact && "flex-col sm:flex-row sm:items-center"
      )}>
        <div className="space-y-1">
          {!isMinimal && (
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-primary/10 p-1.5">
                <BookOpen className="h-4 w-4 text-primary" />
              </div>
              <h2 className={cn(
                "font-bold tracking-tight",
                isCompact ? "text-lg" : "text-2xl"
              )}>
                {title}
              </h2>
              {books.length > 0 && (
                <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                  {books.length}
                </span>
              )}
            </div>
          )}
          
          {!isCompact && subtitle && (
            <p className={cn(
              "text-muted-foreground",
              isMinimal ? "text-sm" : "text-sm"
            )}>
              {subtitle}
            </p>
          )}
        </div>

        {onViewAll && !isMinimal && (
          <Button
            variant={isCompact ? "ghost" : "outline"}
            size={isCompact ? "sm" : "default"}
            onClick={onViewAll}
            className="group shrink-0 transition-all hover:gap-2"
          >
            <span>View All</span>
            <ChevronRight className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </Button>
        )}
      </div>

      {/* Books Grid */}
      <div className={cn(
        !isMinimal && "mt-6",
        isCompact && "mt-4"
      )}>
        {loading ? (
          <div className={cn(
            "grid gap-4",
            isCompact ? "grid-cols-2 sm:grid-cols-3" : "grid-cols-2 sm:grid-cols-3 lg:grid-cols-4"
          )}>
            {Array.from({ length: isCompact ? 3 : 4 }).map((_, index) => (
              <BookSkeleton key={index} />
            ))}
          </div>
        ) : books.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-lg border border-dashed bg-muted/30 py-12">
            <BookOpen className="h-10 w-10 text-muted-foreground/50" />
            <p className="mt-2 text-sm font-medium text-muted-foreground">
              No similar books found
            </p>
            <p className="text-xs text-muted-foreground/70">
              Check back later for recommendations
            </p>
          </div>
        ) : (
          <>
            <div className={cn(
              "grid gap-4",
              isCompact ? "grid-cols-2 sm:grid-cols-3" : "grid-cols-2 sm:grid-cols-3 lg:grid-cols-4"
            )}>
              {displayBooks.map((book) => (
                <div
                  key={book.id}
                  className="group/card relative transition-transform hover:scale-[1.02]"
                >
                  <BookCard
                    book={{
                      id: String(book.id),
                      title: book.title,
                      author: {
                        id: String(book.id),
                        name: book.author,
                      },
                      cover: book.coverUrl ?? undefined,
                      rating: book.rating ?? undefined,
                      publicationYear: book.publicationYear ?? undefined,
                    } as any}
                    href={`/books/${book.id}`}
                    onView={() => onBookClick?.(book)}
                    variant={isCompact ? "compact" : "default"}
                    showActions={false}
                    showGenres={false}
                  />
                  
                  {/* New badge */}
                  {book.isNew && (
                    <div className="absolute -top-2 left-2 z-10 rounded-full bg-primary px-2 py-0.5 text-xs font-medium text-primary-foreground shadow-lg">
                      New
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Load More */}
            {shouldShowLoadMore && (
              <div className="mt-6 flex justify-center">
                <Button
                  variant="outline"
                  onClick={() => setVisibleCount((prev) => prev + maxDisplay)}
                  className="group gap-2 transition-all hover:gap-3"
                >
                  <span>Load More</span>
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </Button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Decorative footer for default variant */}
      {!isMinimal && books.length > 0 && (
        <div className="mt-4 flex items-center gap-2">
          <div className="h-px flex-1 bg-gradient-to-r from-primary/10 to-transparent" />
          <Sparkles className="h-3 w-3 text-muted-foreground/30" />
          <div className="h-px flex-1 bg-gradient-to-l from-primary/10 to-transparent" />
        </div>
      )}
    </section>
  );
}