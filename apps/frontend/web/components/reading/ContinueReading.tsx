"use client";

import Link from "next/link";
import { BookOpen } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { BookCover } from "@/components/books";
import { BookRating } from "@/components/books";
import { BookSkeleton } from "@/components/books";
import { ReadingProgress } from "./ReadingProgress";

interface ContinueReadingBook {
  id: string;
  title: string;
  author: string;
  coverUrl?: string;
  rating?: number;
  progress: number;
  currentPage: number;
  totalPages: number;
  lastReadAt?: string;
  estimatedTimeLeft?: string;
}

interface ContinueReadingProps {
  books: ContinueReadingBook[];
  loading?: boolean;
  className?: string;
  maxDisplay?: number;
}

export function ContinueReading({
  books,
  loading = false,
  className,
  maxDisplay = 6,
}: ContinueReadingProps) {
  const displayBooks = books.slice(0, maxDisplay);
  const hasMore = books.length > maxDisplay;

  return (
    <section className={cn("space-y-5", className)}>
      {/* ====================================================== */}
      {/* Header */}
      {/* ====================================================== */}

      <div className="flex items-center justify-between">
        <div>
          <h2 className="flex items-center gap-2 text-2xl font-bold tracking-tight">
            <BookOpen className="h-5 w-5 text-primary" />
            Continue Reading
          </h2>

          <p className="text-sm text-muted-foreground mt-1">
            {books.length === 0
              ? "Pick up where you left off."
              : `${books.length} book${books.length > 1 ? "s" : ""} waiting for you`}
          </p>
        </div>

        {!loading && books.length > 0 && (
          <Link href="/library/currently-reading">
            <Button variant="outline">
              View All
            </Button>
          </Link>
        )}
      </div>

      {/* ====================================================== */}
      {/* Loading */}
      {/* ====================================================== */}

      {loading && (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((item) => (
            <BookSkeleton key={item} variant="default" />
          ))}
        </div>
      )}

      {/* ====================================================== */}
      {/* Empty State */}
      {/* ====================================================== */}

      {!loading && books.length === 0 && (
        <div className="rounded-2xl border border-dashed border-border bg-card py-14 text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
            <BookOpen className="h-8 w-8 text-primary" />
          </div>

          <h3 className="mt-5 text-lg font-semibold">
            No books in progress
          </h3>

          <p className="mt-2 text-sm text-muted-foreground">
            {/* FIX: Replaced ' with &apos; */}
            Start reading from your library and we&apos;ll automatically
            keep track of your progress.
          </p>

          <div className="mt-6">
            <Link href="/library">
              <Button>
                Browse Library
              </Button>
            </Link>
          </div>
        </div>
      )}

      {/* ====================================================== */}
      {/* Reading Grid */}
      {/* ====================================================== */}

      {!loading && books.length > 0 && (
        <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
                    {displayBooks.map((book) => (
            <div
              key={book.id}
              className="group overflow-hidden rounded-2xl border bg-card transition-all duration-300 hover:-translate-y-1 hover:border-primary/20 hover:shadow-lg"
            >
              <div className="p-5">
                <div className="flex gap-4">
                  {/* Cover */}
                  <Link href={`/books/${book.id}`} className="shrink-0">
                    <BookCover
                      src={book.coverUrl}
                      alt={book.title}
                      width={100}
                      height={145}
                      className="rounded-lg transition-transform duration-300 group-hover:scale-[1.03]"
                    />
                  </Link>

                  {/* Details */}
                  <div className="flex flex-1 flex-col justify-between min-w-0">
                    <div className="space-y-2">
                      <Link href={`/books/${book.id}`}>
                        <h3 className="line-clamp-2 font-semibold transition-colors hover:text-primary">
                          {book.title}
                        </h3>
                      </Link>

                      <p className="text-sm text-muted-foreground">
                        {book.author}
                      </p>

                      <BookRating
                        rating={book.rating ?? 0}
                        ratingsCount={0}
                        size="sm"
                        showStars
                      />

                      <ReadingProgress
                        progress={book.progress}
                        currentPage={book.currentPage}
                        totalPages={book.totalPages}
                        estimatedTimeLeft={book.estimatedTimeLeft}
                        lastReadAt={book.lastReadAt}
                      />
                    </div>

                    <div className="mt-4 flex items-center justify-between">
                      <div className="text-xs text-muted-foreground">
                        Page{" "}
                        <span className="font-medium text-foreground">
                          {book.currentPage}
                        </span>{" "}
                        of{" "}
                        <span className="font-medium text-foreground">
                          {book.totalPages}
                        </span>
                      </div>

                      <Link href={`/books/${book.id}`}>
                        <Button size="sm">
                          Continue
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ====================================================== */}
      {/* Footer */}
      {/* ====================================================== */}

      {!loading && hasMore && (
        <div className="flex justify-center pt-2">
          <Link href="/library/currently-reading">
            <Button variant="outline" size="lg">
              View all {books.length} books
            </Button>
          </Link>
        </div>
      )}
    </section>
  );
}