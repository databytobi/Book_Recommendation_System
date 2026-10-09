"use client";

import Link from "next/link";
import {
  ArrowRight,
  Clock,
  Eye,
  History,
  Sparkles,
  Trash2,
} from "lucide-react";
import { format, formatDistanceToNow } from "date-fns";

import { cn } from "@/lib/utils";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

import {
  BookCard,
  BookSkeleton,
} from "@/components/books";

interface RecentlyViewedBook {
  id: string;
  title: string;
  author: string;
  coverUrl?: string;
  rating?: number;
  viewedAt: string;
  progress?: number;
  isInLibrary?: boolean;
}

interface RecentlyViewedProps {
  books: RecentlyViewedBook[];
  loading?: boolean;
  className?: string;
  maxDisplay?: number;
  showClearAll?: boolean;
  onClearAll?: () => void;
  onBookClick?: (book: RecentlyViewedBook) => void;
}

function formatViewedTime(dateString: string) {
  try {
    const viewed = new Date(dateString);
    const hours =
      (Date.now() - viewed.getTime()) / 1000 / 60 / 60;

    if (hours < 1) return "Just now";

    if (hours < 24)
      return formatDistanceToNow(viewed, {
        addSuffix: true,
      });

    return format(viewed, "MMM d, yyyy");
  } catch {
    return "Recently";
  }
}

function getViewedBadge(dateString: string) {
  try {
    const viewed = new Date(dateString);

    const hours =
      (Date.now() - viewed.getTime()) / 1000 / 60 / 60;

    if (hours < 1)
      return {
        label: "Just now",
        variant: "default" as const,
      };

    if (hours < 24)
      return {
        label: "Today",
        variant: "secondary" as const,
      };

    if (hours < 24 * 7)
      return {
        label: "This week",
        variant: "outline" as const,
      };

    return {
      label: "Older",
      variant: "secondary" as const,
    };
  } catch {
    return {
      label: "Recent",
      variant: "secondary" as const,
    };
  }
}

export function RecentlyViewed({
  books,
  loading = false,
  className,
  maxDisplay = 6,
  showClearAll = true,
  onClearAll,
  onBookClick,
}: RecentlyViewedProps) {
  const displayBooks = books.slice(0, maxDisplay);

  const hasMore = books.length > maxDisplay;

  return (
    <section className={cn("space-y-6", className)}>
      {/* Header */}

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

        <div>
          <h2 className="flex items-center gap-2 text-2xl font-bold tracking-tight">
            <Eye className="h-5 w-5 text-primary" />
            Recently Viewed
          </h2>

          <p className="mt-1 text-sm text-muted-foreground">
            Books you&apos;ve explored recently.
          </p>
        </div>

        <div className="flex items-center gap-2">

          {showClearAll &&
            !loading &&
            books.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onClearAll}
                className="text-muted-foreground hover:text-destructive"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Clear history
              </Button>
            )}

          <Button
            variant="ghost"
            size="sm"
          >
            <Link
              href="/library/history"
              className="flex items-center gap-2"
            >
              View history
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>

        </div>
      </div>

      {/* Quick Stats */}

      {!loading && books.length > 0 && (

        <div className="flex flex-wrap gap-3">

          <Badge
            variant="secondary"
            className="gap-1"
          >
            <History className="h-3 w-3" />
            {books.length} books viewed
          </Badge>

          <Badge
            variant="outline"
            className="gap-1"
          >
            <Clock className="h-3 w-3" />
            Last viewed{" "}
            {formatViewedTime(displayBooks[0].viewedAt)}
          </Badge>

        </div>

      )}

      {/* Loading */}

      {loading && (

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">

          {[1, 2, 3, 4].map((item) => (
            <BookSkeleton
              key={item}
              variant="default"
            />
          ))}

        </div>

      )}

      {/* Empty */}

      {!loading &&
        books.length === 0 && (

          <Card className="border-dashed">

            <CardContent className="flex flex-col items-center justify-center py-14 text-center">

              <div className="rounded-full bg-muted/50 p-5">
                <Eye className="h-8 w-8 text-muted-foreground" />
              </div>

              <h3 className="mt-5 text-lg font-semibold">
                Nothing viewed yet
              </h3>

              <p className="mt-2 max-w-sm text-sm text-muted-foreground">
                Browse books and they&apos;ll automatically appear here
                so you can jump back into them anytime.
              </p>

              <Button className="mt-6">

                <Link
                  href="/discover"
                  className="flex items-center gap-2"
                >
                  <Sparkles className="h-4 w-4" />
                  Discover Books
                </Link>

              </Button>

            </CardContent>

          </Card>

      )}
      
      {/* Books Grid */}

      {!loading && books.length > 0 && (

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">

          {displayBooks.map((book) => {

            const badge = getViewedBadge(book.viewedAt);

            return (

              <Card
                key={book.id}
                onClick={() => onBookClick?.(book)}
                className={cn(
                  "group cursor-pointer overflow-hidden transition-all duration-300",
                  "hover:-translate-y-1 hover:border-primary/20 hover:shadow-xl"
                )}
              >

                <div className="relative">

                  <BookCard
                    book={{
                      id: book.id,
                      title: book.title,
                      author: {
                        id: book.id,
                        name: book.author,
                      },
                      coverImage: book.coverUrl,
                      averageRating: book.rating ?? 0,
                      ratingsCount: 0,
                      genres: [],
                      isFavorite: false,
                      isInLibrary: book.isInLibrary ?? false,
                    } as any}
                    href={`/books/${book.id}`}
                    variant="default"
                    size="md"
                    showGenres={false}
                    showProgress={false}
                    showActions={true}
                  />

                  {/* Time Badge */}

                  <div className="absolute right-3 top-3">

                    <TooltipProvider>

                      <Tooltip>

                        <TooltipTrigger>

                          <Badge
                            variant={badge.variant}
                            className="gap-1 bg-background/90 backdrop-blur"
                          >
                            <Clock className="h-3 w-3" />
                            {badge.label}
                          </Badge>

                        </TooltipTrigger>

                        <TooltipContent>
                          Viewed {formatViewedTime(book.viewedAt)}
                        </TooltipContent>

                      </Tooltip>

                    </TooltipProvider>

                  </div>

                  {/* Reading Progress */}

                  {book.progress !== undefined &&
                    book.progress > 0 &&
                    book.progress < 100 && (

                      <div className="absolute bottom-0 left-0 right-0 h-1 bg-muted">

                        <div
                          className="h-full rounded-full bg-gradient-to-r from-primary to-violet-500 transition-all duration-700"
                          style={{
                            width: `${book.progress}%`,
                          }}
                        />

                      </div>

                  )}

                </div>

                <CardFooter className="p-4 pt-3">

                  <div className="flex w-full items-center justify-between">

                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground">

                      <Clock className="h-3.5 w-3.5" />

                      <span>
                        {formatViewedTime(book.viewedAt)}
                      </span>

                    </div>

                    <Button
                      variant="ghost"
                      size="sm"
                      className="opacity-0 transition-opacity duration-200 group-hover:opacity-100"
                    >
                      <Link
                        href={`/books/${book.id}`}
                        className="flex items-center gap-1"
                      >
                        View

                        <ArrowRight className="h-3.5 w-3.5" />

                      </Link>
                    </Button>

                  </div>

                </CardFooter>

              </Card>

            );

          })}

        </div>

      )}

      {/* View More */}

      {!loading && hasMore && (

        <div className="flex justify-center">

          <Button
            variant="outline"
            size="lg"
          >
            <Link
              href="/library/history"
              className="flex items-center gap-2"
            >
              View all {books.length} books

              <ArrowRight className="h-4 w-4" />

            </Link>
          </Button>

        </div>

      )}

    </section>
  );
}