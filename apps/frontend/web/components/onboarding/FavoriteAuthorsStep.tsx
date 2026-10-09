"use client";

import { useState } from "react";
import Image from "next/image";
import { Check, Loader2, User } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface Author {
  id: number;
  name: string;
  image_url?: string | null;
  books_count?: number;
}

interface FavoriteAuthorsStepProps {
  authors: Author[];
  loading?: boolean;
  error?: string | null;
  initialSelection?: number[];
  minimumSelection?: number;
  onContinue: (selectedAuthorIds: number[]) => void;
  onRetry?: () => void;
  className?: string;
}

export function FavoriteAuthorsStep({
  authors,
  loading = false,
  error = null,
  initialSelection = [],
  minimumSelection = 3,
  onContinue,
  onRetry,
  className,
}: FavoriteAuthorsStepProps) {
  const [selected, setSelected] = useState<number[]>(initialSelection);

  const toggleAuthor = (id: number) => {
    setSelected((previous) => {
      if (previous.includes(id)) {
        return previous.filter((item) => item !== id);
      }

      return [...previous, id];
    });
  };

  if (loading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center text-center">
        <h2 className="text-2xl font-bold">Unable to load authors</h2>

        <p className="mt-2 text-sm text-muted-foreground">
          {error}
        </p>

        {onRetry && (
          <Button className="mt-5" onClick={onRetry}>
            Try Again
          </Button>
        )}
      </div>
    );
  }

  return (
    <div className={cn("w-full space-y-8", className)}>
      <div className="text-center">
        <h2 className="text-3xl font-bold">
          Choose Your Favorite Authors
        </h2>

        <p className="mt-3 text-muted-foreground">
          Select at least {minimumSelection} authors you enjoy.
          We&apos;ll use them to personalize your recommendations.
        </p>
      </div>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {authors.map((author) => {
          const active = selected.includes(author.id);

          return (
            <button
              key={author.id}
              type="button"
              onClick={() => toggleAuthor(author.id)}
              aria-pressed={active}
              className={cn(
                "group relative rounded-2xl border bg-card p-5 text-center transition-all duration-200",
                active
                  ? "border-primary ring-2 ring-primary/20"
                  : "hover:border-primary/30 hover:shadow-md"
              )}
            >
              {active && (
                <div className="absolute right-3 top-3 flex h-6 w-6 items-center justify-center rounded-full bg-primary text-primary-foreground">
                  <Check className="h-4 w-4" />
                </div>
              )}

              {author.image_url ? (
                <Image
                  src={author.image_url}
                  alt={author.name}
                  width={90}
                  height={90}
                  className="mx-auto rounded-full object-cover"
                />
              ) : (
                <div className="mx-auto flex h-[90px] w-[90px] items-center justify-center rounded-full bg-primary/10">
                  <User className="h-10 w-10 text-primary" />
                </div>
              )}

              <h3 className="mt-4 font-semibold">
                {author.name}
              </h3>

              {author.books_count !== undefined && (
                <p className="mt-1 text-sm text-muted-foreground">
                  {author.books_count} books
                </p>
              )}
            </button>
          );
        })}
      </div>

      <div className="flex items-center justify-between border-t pt-6">
        <p className="text-sm text-muted-foreground">
          {selected.length} selected
        </p>

        <Button
          type="button"
          disabled={selected.length < minimumSelection}
          onClick={() => onContinue(selected)}
        >
          Continue
        </Button>
      </div>
    </div>
  );
}

export type { FavoriteAuthorsStepProps };