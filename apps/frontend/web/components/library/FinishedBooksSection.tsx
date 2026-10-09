// apps/frontend/web/components/library/FinishedBooksSection.tsx

"use client";

import {
  ArrowRight,
  CheckCircle2,
} from "lucide-react";

import { BookCard } from "@/components/books";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Book } from "@/lib/types";

interface FinishedBooksSectionProps {
  books: Book[];
  className?: string;
  onViewAll?: () => void;
}

export function FinishedBooksSection({
  books,
  className,
  onViewAll,
}: FinishedBooksSectionProps) {
  if (books.length === 0) {
    return (
      <section
        className={cn(
          "rounded-2xl border border-dashed bg-card p-10",
          className
        )}
      >
        <div className="flex flex-col items-center justify-center text-center">
          <div className="rounded-full bg-violet-500/10 p-4">
            <CheckCircle2 className="h-8 w-8 text-violet-500" />
          </div>

          <h2 className="mt-4 text-xl font-semibold">
            Finished Books
          </h2>

          <p className="mt-2 max-w-md text-sm text-muted-foreground">
            {/* FIX: Replaced ' with &apos; */}
            You haven&apos;t finished any books yet.
            Once you complete a book it will appear here.
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
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-violet-500" />

            <h2 className="text-2xl font-bold tracking-tight">
              Finished Reading
            </h2>
          </div>

          <p className="mt-1 text-sm text-muted-foreground">
            {/* FIX: Replaced ' with &apos; */}
            Books you&apos;ve successfully completed.
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
          lg:grid-cols-3
          xl:grid-cols-4
        "
      >
        {books.map((book) => (
          <BookCard
            key={book.id}
            book={book as any}
            variant="default"
            showActions
            showGenres
            showDescription={false}
          />
        ))}
      </div>
    </section>
  );
}

export type {
  FinishedBooksSectionProps,
};