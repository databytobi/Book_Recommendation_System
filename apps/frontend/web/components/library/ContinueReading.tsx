// apps/frontend/web/components/library/ContinueReading.tsx

"use client";

import { ArrowRight, BookOpen } from "lucide-react";

import { Book } from "@/lib/types";
import { BookCard } from "@/components/books";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ContinueReadingBook extends Book {
  progress: number;
  lastReadAt?: string;
  rating?: number | undefined;
}

interface ContinueReadingProps {
  books: ContinueReadingBook[];
  className?: string;
  onViewAll?: () => void;
}

export function ContinueReading({
  books,
  className,
  onViewAll,
}: ContinueReadingProps) {
  if (books.length === 0) {
    return (
      <section
        className={cn(
          "rounded-2xl border border-dashed bg-card p-10",
          className
        )}
      >
        <div className="flex flex-col items-center justify-center text-center">
          <div className="rounded-full bg-primary/10 p-4">
            <BookOpen className="h-8 w-8 text-primary" />
          </div>

          <h2 className="mt-4 text-xl font-semibold">
            Continue Reading
          </h2>

          <p className="mt-2 max-w-md text-sm text-muted-foreground">
            {/* FIX: Replaced ' with &apos; */}
            You don&apos;t have any books in progress yet.
            Start reading a book and it will appear here.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className={cn("space-y-6", className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">
            Continue Reading
          </h2>

          <p className="text-sm text-muted-foreground">
            Pick up where you left off.
          </p>
        </div>

        {onViewAll && (
          <Button
            variant="ghost"
            onClick={onViewAll}
            className="group"
          >
            View All

            <ArrowRight className="ml-2 h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" />
          </Button>
        )}
      </div>

      {/* Books */}
      <div
        className="
          grid
          gap-6
          sm:grid-cols-2
          xl:grid-cols-3
        "
      >
        {books.map((book) => (
          <BookCard
            key={book.id}
            book={book as any}
            variant="horizontal"
            showProgress
            showActions
            showGenres={false}
            showDescription={false}
          />
        ))}
      </div>
    </section>
  );
}

export type {
  ContinueReadingBook,
  ContinueReadingProps,
};