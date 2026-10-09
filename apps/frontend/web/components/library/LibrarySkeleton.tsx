
// apps/frontend/web/components/library/LibrarySkeleton.tsx

"use client";

import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface LibrarySkeletonProps {
  className?: string;
}

function BookCardSkeleton() {
  return (
    <div className="overflow-hidden rounded-2xl border bg-card">
      <Skeleton className="aspect-[2/3] w-full rounded-none" />

      <div className="space-y-3 p-4">
        <Skeleton className="h-5 w-4/5" />

        <Skeleton className="h-4 w-2/3" />

        <Skeleton className="h-4 w-24" />

        <div className="flex gap-2 pt-2">
          <Skeleton className="h-6 w-16 rounded-full" />
          <Skeleton className="h-6 w-14 rounded-full" />
        </div>

        <div className="flex justify-between pt-3">
          <Skeleton className="h-9 w-9 rounded-full" />
          <Skeleton className="h-9 w-9 rounded-full" />
          <Skeleton className="h-9 w-9 rounded-full" />
          <Skeleton className="h-9 w-9 rounded-full" />
        </div>
      </div>
    </div>
  );
}

function SectionSkeleton() {
  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-7 w-56" />
          <Skeleton className="h-4 w-72" />
        </div>

        <Skeleton className="h-10 w-28 rounded-lg" />
      </div>

      <div
        className="
          grid
          gap-6
          sm:grid-cols-2
          lg:grid-cols-3
          xl:grid-cols-4
        "
      >
        {Array.from({ length: 4 }).map((_, index) => (
          <BookCardSkeleton key={index} />
        ))}
      </div>
    </section>
  );
}

export function LibrarySkeleton({
  className,
}: LibrarySkeletonProps) {
  return (
    <div
      className={cn(
        "space-y-10",
        className
      )}
    >
      {/* Library Header */}
      <section className="rounded-2xl border bg-card p-6">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="space-y-3">
            <Skeleton className="h-9 w-56" />
            <Skeleton className="h-5 w-96 max-w-full" />
          </div>

          <Skeleton className="h-11 w-40 rounded-lg" />
        </div>

        <div className="my-6 h-px bg-border" />

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <div
              key={index}
              className="rounded-xl border p-5"
            >
              <div className="flex items-start justify-between">
                <div className="space-y-3">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-8 w-14" />
                </div>

                <Skeleton className="h-12 w-12 rounded-xl" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Continue Reading */}
      <SectionSkeleton />

      {/* Favorites */}
      <SectionSkeleton />
    </div>
  );
}

export type {
  LibrarySkeletonProps,
};
