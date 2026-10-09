"use client";

import Image from "next/image";
// FIX 2 & 3: Replaced Clock with Languages, removed unused Users
import { Calendar, BookOpen, Languages } from "lucide-react";

import { BookRating } from "@/components/books";
import { cn } from "@/lib/utils";

interface BookHeaderProps {
  title: string;
  author: string;
  coverUrl?: string;
  averageRating: number;
  ratingsCount: number;
  publicationYear?: number;
  genres?: string[];
  className?: string;
  actions?: React.ReactNode;
  pageCount?: number;
  language?: string;
  series?: string;
  edition?: string;
  description?: string;
}

export function BookHeader({
  title,
  author,
  coverUrl,
  averageRating,
  ratingsCount,
  publicationYear,
  genres = [],
  className,
  actions,
  pageCount,
  language,
  series,
  edition,
  description,
}: BookHeaderProps) {
  return (
    <section
      className={cn(
        "group relative flex flex-col gap-8 rounded-2xl border bg-card p-6 transition-all hover:shadow-lg hover:shadow-primary/5 lg:flex-row lg:p-8",
        className
      )}
    >
      {/* Decorative gradient background */}
      <div className="absolute inset-0 -z-10 overflow-hidden rounded-2xl">
        <div className="absolute -right-32 -top-32 h-64 w-64 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute -bottom-32 -left-32 h-64 w-64 rounded-full bg-secondary/5 blur-3xl" />
      </div>

      {/* Book Cover */}
      <div className="flex flex-shrink-0 justify-center lg:block">
        <div className="group/cover relative overflow-hidden rounded-2xl border bg-muted shadow-lg transition-all hover:shadow-xl hover:shadow-primary/10">
          {coverUrl ? (
            <>
              <Image
                src={coverUrl}
                alt={title}
                width={240}
                height={360}
                className="h-[360px] w-[240px] object-cover transition-transform duration-300 group-hover/cover:scale-105"
              />
              {/* FIX 1: Removed fake hover buttons - now just a subtle overlay */}
              <div className="absolute inset-0 bg-black/0 opacity-0 transition-opacity duration-300 group-hover/cover:opacity-100" />
            </>
          ) : (
            <div className="flex h-[360px] w-[240px] flex-col items-center justify-center bg-gradient-to-br from-muted to-muted/50 text-muted-foreground">
              <BookOpen className="mb-2 h-12 w-12 opacity-30" />
              <span className="text-sm font-medium">No Cover</span>
            </div>
          )}
          
          {/* Status badge */}
          {edition && (
            <div className="absolute right-2 top-2 rounded-full bg-primary/90 px-2.5 py-0.5 text-xs font-medium text-primary-foreground backdrop-blur-sm">
              {edition}
            </div>
          )}
        </div>
      </div>

      {/* Book Information */}
      <div className="flex flex-1 flex-col">
        {/* Title & Author */}
        <div>
          {series && (
            <p className="text-sm font-medium text-primary">
              {series}
            </p>
          )}
          <h1 className="text-3xl font-bold tracking-tight transition-colors lg:text-4xl group-hover:text-primary">
            {title}
          </h1>
          <p className="mt-2 text-lg text-muted-foreground">
            by{" "}
            <span className="font-medium text-foreground transition-colors hover:text-primary">
              {author}
            </span>
          </p>
        </div>

        {/* Description */}
        {description && (
          <p className="mt-3 line-clamp-3 text-sm leading-relaxed text-muted-foreground">
            {description}
          </p>
        )}

        {/* Rating Section */}
        <div className="mt-4 flex items-center gap-4">
          <BookRating
            rating={averageRating}
            ratingsCount={ratingsCount}
            size="lg"
          />
          {ratingsCount > 0 && (
            <span className="text-sm text-muted-foreground">
              ({ratingsCount.toLocaleString()} ratings)
            </span>
          )}
        </div>

        {/* Metadata Grid */}
        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3">
          {publicationYear && (
            <div className="flex items-center gap-2 rounded-lg bg-secondary/50 px-3 py-2">
              <Calendar className="h-4 w-4 text-primary" />
              <div>
                <p className="text-xs text-muted-foreground">Published</p>
                <p className="text-sm font-medium">{publicationYear}</p>
              </div>
            </div>
          )}

          {pageCount && (
            <div className="flex items-center gap-2 rounded-lg bg-secondary/50 px-3 py-2">
              <BookOpen className="h-4 w-4 text-primary" />
              <div>
                <p className="text-xs text-muted-foreground">Pages</p>
                <p className="text-sm font-medium">{pageCount.toLocaleString()}</p>
              </div>
            </div>
          )}

          {language && (
            <div className="flex items-center gap-2 rounded-lg bg-secondary/50 px-3 py-2">
              {/* FIX 2: Replaced Clock with Languages */}
              <Languages className="h-4 w-4 text-primary" />
              <div>
                <p className="text-xs text-muted-foreground">Language</p>
                <p className="text-sm font-medium">{language}</p>
              </div>
            </div>
          )}
        </div>

        {/* Genres */}
        {genres.length > 0 && (
          <div className="mt-6 flex flex-wrap gap-2">
            {genres.slice(0, 5).map((genre) => (
              <span
                key={genre}
                className="rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary transition-colors hover:bg-primary/20"
              >
                {genre}
              </span>
            ))}
            {genres.length > 5 && (
              <span className="rounded-full bg-muted px-3 py-1 text-sm font-medium text-muted-foreground">
                +{genres.length - 5} more
              </span>
            )}
          </div>
        )}

        {/* Actions */}
        {actions && (
          <div className="mt-6 border-t border-border/50 pt-6">
            {actions}
          </div>
        )}
      </div>
    </section>
  );
}