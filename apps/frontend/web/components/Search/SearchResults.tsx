"use client";

import {
  List,
  LayoutGrid,
  ArrowUpDown,
  BookOpen,
  Sparkles,
  ArrowRight,
} from "lucide-react";
import { useState } from "react";
import Image from "next/image";

import { BookCard, BookSkeleton } from "@/components/books";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface SearchBook {
  id: number | string;
  title: string;
  author: string;
  coverUrl?: string;
  rating?: number;
  publicationYear?: number;
  genre?: string;
  isNew?: boolean;
}

interface SearchResultsProps {
  books: SearchBook[];
  loading?: boolean;
  className?: string;
  onBookClick?: (book: SearchBook) => void;
  totalResults?: number;
  sortOptions?: { label: string; value: string }[];
  onSort?: (value: string) => void;
  onViewAll?: () => void;
}

export function SearchResults({
  books,
  loading = false,
  className,
  onBookClick,
  totalResults,
  sortOptions = [
    { label: "Relevance", value: "relevance" },
    { label: "Newest", value: "newest" },
    { label: "Highest Rated", value: "rating" },
    { label: "Most Popular", value: "popular" },
  ],
  onSort,
  onViewAll,
}: SearchResultsProps) {
  const [gridView, setGridView] = useState(true);
  const [isSortOpen, setIsSortOpen] = useState(false);
  const [selectedSort, setSelectedSort] = useState(sortOptions[0]?.value || "relevance");

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="h-5 w-32 animate-pulse rounded bg-muted" />
          <div className="flex gap-2">
            <div className="h-10 w-10 animate-pulse rounded bg-muted" />
            <div className="h-10 w-10 animate-pulse rounded bg-muted" />
          </div>
        </div>

        <div
          className={cn(
            "grid gap-6",
            gridView
              ? "grid-cols-2 sm:grid-cols-3 lg:grid-cols-4"
              : "grid-cols-1",
            className
          )}
        >
          {Array.from({ length: gridView ? 8 : 4 }).map((_, index) => (
            <BookSkeleton key={index} />
          ))}
        </div>
      </div>
    );
  }

  if (books.length === 0) {
    return null;
  }

  const displayTotal = totalResults || books.length;

  return (
    <section
      className={cn(
        "space-y-6",
        className
      )}
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-primary/10 p-1.5">
            <BookOpen className="h-4 w-4 text-primary" />
          </div>
          <div>
            <p className="text-sm font-medium">
              <span className="text-foreground">{displayTotal.toLocaleString()}</span>
              <span className="text-muted-foreground"> books found</span>
            </p>
            {onViewAll && (
              <p className="text-xs text-muted-foreground/70">
                Showing {books.length} results
              </p>
            )}
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {onSort && (
            <div className="relative">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsSortOpen(!isSortOpen)}
                className="gap-2"
              >
                <ArrowUpDown className="h-4 w-4" />
                <span className="hidden sm:inline">
                  {sortOptions.find((o) => o.value === selectedSort)?.label || "Sort"}
                </span>
              </Button>

              {isSortOpen && (
                <div className="absolute right-0 top-full z-50 mt-1 min-w-[160px] rounded-xl border bg-popover p-1 shadow-lg">
                  {sortOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => {
                        setSelectedSort(option.value);
                        onSort(option.value);
                        setIsSortOpen(false);
                      }}
                      className={cn(
                        "flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-primary/10",
                        selectedSort === option.value && "bg-primary/10 text-primary"
                      )}
                    >
                      <span className="flex-1 text-left">{option.label}</span>
                      {selectedSort === option.value && (
                        <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="flex rounded-lg border bg-card p-0.5">
            <Button
              size="icon"
              variant={gridView ? "default" : "ghost"}
              onClick={() => setGridView(true)}
              className={cn(
                "h-8 w-8 rounded-md",
                gridView && "shadow-sm"
              )}
            >
              <LayoutGrid className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant={!gridView ? "default" : "ghost"}
              onClick={() => setGridView(false)}
              className={cn(
                "h-8 w-8 rounded-md",
                !gridView && "shadow-sm"
              )}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {gridView ? (
        <div className={cn(
          "grid gap-4 sm:gap-6",
          "grid-cols-2 sm:grid-cols-3 lg:grid-cols-4"
        )}>
          {books.map((book, index) => (
            <div
              key={book.id}
              className="animate-fade-in group/card relative transition-transform hover:scale-[1.02]"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <BookCard
                book={{
                  id: String(book.id),
                  title: book.title,
                  author: {
                    id: String(book.id),
                    name: book.author,
                  },
                  authors: [book.author],
                  coverImage: book.coverUrl,
                  averageRating: book.rating || 0,
                  ratingsCount: 0,
                  publicationYear: book.publicationYear,
                  genres: book.genre ? [book.genre] : [],
                  isFavorite: false,
                  isInLibrary: false,
                }}
                href={`/books/${book.id}`}
                variant="default"
                size="md"
                showActions={false}
                showGenres={false}
              />

              {book.isNew && (
                <div className="absolute -top-2 left-2 z-10 rounded-full bg-primary px-2 py-0.5 text-xs font-medium text-primary-foreground shadow-lg">
                  New
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {books.map((book, index) => (
            <div
              key={book.id}
              className="animate-fade-in group relative rounded-xl border bg-card p-4 transition-all hover:border-primary/30 hover:shadow-md hover:shadow-primary/5"
              style={{ animationDelay: `${index * 30}ms` }}
            >
              <button
                onClick={() => onBookClick?.(book)}
                className="flex w-full items-center gap-4 text-left"
              >
                <div className="shrink-0">
                  {book.coverUrl ? (
                    <Image
                      src={book.coverUrl}
                      alt={book.title}
                      width={64}
                      height={96}
                      className="h-24 w-16 rounded-lg object-cover transition-transform group-hover:scale-105"
                    />
                  ) : (
                    <div className="flex h-24 w-16 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                      <BookOpen className="h-6 w-6 opacity-30" />
                    </div>
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="font-semibold transition-colors group-hover:text-primary">
                        {book.title}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {book.author}
                      </p>
                    </div>
                    {book.rating && (
                      <div className="flex items-center gap-1 rounded-full bg-yellow-50 px-2 py-0.5 text-xs font-medium text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400">
                        <span>⭐</span>
                        <span>{book.rating.toFixed(1)}</span>
                      </div>
                    )}
                  </div>

                  <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                    {book.publicationYear && (
                      <span>{book.publicationYear}</span>
                    )}
                    {book.genre && (
                      <>
                        <span>•</span>
                        <span>{book.genre}</span>
                      </>
                    )}
                  </div>
                </div>
              </button>

              <div className="absolute right-4 top-1/2 -translate-y-1/2 opacity-0 transition-all group-hover:opacity-100 group-hover:translate-x-1">
                <ArrowRight className="h-5 w-5 text-primary" />
              </div>
            </div>
          ))}
        </div>
      )}

      {onViewAll && books.length < (totalResults || 0) && (
        <div className="flex justify-center pt-4">
          <Button
            variant="outline"
            onClick={onViewAll}
            className="group gap-2 transition-all hover:gap-3"
          >
            <span>View All {totalResults?.toLocaleString()} Results</span>
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </Button>
        </div>
      )}

      {books.length > 0 && (
        <div className="flex items-center gap-2 pt-2">
          <div className="h-px flex-1 bg-gradient-to-r from-transparent to-muted" />
          <div className="flex items-center gap-1 text-[10px] text-muted-foreground/50">
            <Sparkles className="h-3 w-3" />
            <span>End of results</span>
          </div>
          <div className="h-px flex-1 bg-gradient-to-l from-transparent to-muted" />
        </div>
      )}
    </section>
  );
}