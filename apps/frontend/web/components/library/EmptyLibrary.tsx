// apps/frontend/web/components/library/EmptyLibrary.tsx

"use client";

import {
  BookOpen,
  Library,
  ArrowRight,
  Sparkles,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface EmptyLibraryProps {
  className?: string;
  onBrowseBooks?: () => void;
}

export function EmptyLibrary({
  className,
  onBrowseBooks,
}: EmptyLibraryProps) {
  return (
    <section
      className={cn(
        "relative overflow-hidden rounded-3xl border bg-card p-10 md:p-16",
        className
      )}
    >
      {/* Background decoration */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute -left-24 -top-24 h-64 w-64 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute -right-24 -bottom-24 h-64 w-64 rounded-full bg-secondary/5 blur-3xl" />
      </div>

      <div className="mx-auto flex max-w-2xl flex-col items-center text-center">
        {/* Icon */}
        <div className="flex h-24 w-24 items-center justify-center rounded-full bg-primary/10">
          <Library className="h-12 w-12 text-primary" />
        </div>

        {/* Title */}
        <h1 className="mt-8 text-4xl font-bold tracking-tight">
          Your Library is Empty
        </h1>

        {/* Description */}
        <p className="mt-4 text-lg leading-8 text-muted-foreground">
          {/* FIX: Replaced ' with &apos; */}
          Discover books you&apos;ll love, save them to your collection,
          and keep track of your reading journey all in one place.
        </p>

        {/* Features */}
        <div className="mt-10 grid w-full gap-4 md:grid-cols-3">
          <div className="rounded-xl border bg-background/50 p-5">
            <BookOpen className="mx-auto h-7 w-7 text-primary" />

            <h3 className="mt-3 font-semibold">
              Discover
            </h3>

            <p className="mt-2 text-sm text-muted-foreground">
              Browse thousands of books recommended just for you.
            </p>
          </div>

          <div className="rounded-xl border bg-background/50 p-5">
            <Sparkles className="mx-auto h-7 w-7 text-primary" />

            <h3 className="mt-3 font-semibold">
              Save
            </h3>

            <p className="mt-2 text-sm text-muted-foreground">
              Build your personal reading collection with one click.
            </p>
          </div>

          <div className="rounded-xl border bg-background/50 p-5">
            <Library className="mx-auto h-7 w-7 text-primary" />

            <h3 className="mt-3 font-semibold">
              Track
            </h3>

            <p className="mt-2 text-sm text-muted-foreground">
              Monitor your progress and revisit your favorite books.
            </p>
          </div>
        </div>

        {/* CTA */}
        <Button
          size="lg"
          className="mt-10 group"
          onClick={onBrowseBooks}
        >
          Browse Books

          <ArrowRight className="ml-2 h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" />
        </Button>
      </div>
    </section>
  );
}

export type {
  EmptyLibraryProps,
};