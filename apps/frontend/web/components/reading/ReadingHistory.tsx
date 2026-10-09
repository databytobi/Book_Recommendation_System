"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import {
  CalendarDays,
  Star,
  ChevronRight,
  BookOpen,
  Clock,
  Search,
  Filter,
  ArrowUpDown,
  Library,
  Award,
  TrendingUp,
} from "lucide-react";

import { format, formatDistanceToNow } from "date-fns";

import { cn } from "@/lib/utils";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";

export interface ReadingHistoryItem {
  id: number | string;
  title: string;
  author: string;
  cover?: string;
  completedAt: string;
  rating: number;
  progress?: number;
  pagesRead?: number;
  totalPages?: number;
  timeSpent?: string;
}

interface ReadingHistoryProps {
  books: ReadingHistoryItem[];
  className?: string;
  showStats?: boolean;
  showSearch?: boolean;
  maxDisplay?: number;
}

type SortOption =
  | "recent"
  | "oldest"
  | "rating"
  | "title";

type FilterOption =
  | "all"
  | "this-month"
  | "this-year"
  | "last-30-days";

export function ReadingHistory({
  books,
  className,
  showStats = true,
  showSearch = true,
  maxDisplay = 10,
}: ReadingHistoryProps) {

  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<SortOption>("recent");
  const [filterBy, setFilterBy] = useState<FilterOption>("all");

  // FIX: Use a ref or move date calculation inside useMemo
  // Instead of using useMemo for now, we'll calculate inside each useMemo
  // This avoids the React Compiler warning

  /* -------------------------------- */
  /* Date Formatter                   */
  /* -------------------------------- */

  const formatDate = (dateString: string, currentDate: Date) => {
    try {
      const date = new Date(dateString);
      const diffDays = (currentDate.getTime() - date.getTime()) / (1000 * 60 * 60 * 24);

      if (diffDays < 1) return "Today";
      if (diffDays < 2) return "Yesterday";
      if (diffDays < 7) return formatDistanceToNow(date, { addSuffix: true });
      return format(date, "MMM d, yyyy");
    } catch {
      return dateString;
    }
  };

  /* -------------------------------- */
  /* Stars                            */
  /* -------------------------------- */

  const renderStars = (rating: number) => (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <Star
          key={star}
          className={cn(
            "h-3.5 w-3.5",
            star <= rating
              ? "fill-yellow-400 text-yellow-400"
              : "fill-muted text-muted"
          )}
        />
      ))}
    </div>
  );

  /* -------------------------------- */
  /* Books (Memoized)                 */
  /* -------------------------------- */

  const displayBooks = useMemo(() => {
    const now = new Date(); // Calculate inside the memo
    let filtered = [...books];

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (book) =>
          book.title.toLowerCase().includes(query) ||
          book.author.toLowerCase().includes(query)
      );
    }

    switch (filterBy) {
      case "this-month":
        filtered = filtered.filter((book) => {
          const d = new Date(book.completedAt);
          return (
            d.getMonth() === now.getMonth() &&
            d.getFullYear() === now.getFullYear()
          );
        });
        break;

      case "this-year":
        filtered = filtered.filter((book) => {
          const d = new Date(book.completedAt);
          return d.getFullYear() === now.getFullYear();
        });
        break;

      case "last-30-days":
        filtered = filtered.filter((book) => {
          const d = new Date(book.completedAt);
          return (now.getTime() - d.getTime()) / (1000 * 60 * 60 * 24) <= 30;
        });
        break;
    }

    switch (sortBy) {
      case "recent":
        filtered.sort(
          (a, b) =>
            new Date(b.completedAt).getTime() -
            new Date(a.completedAt).getTime()
        );
        break;

      case "oldest":
        filtered.sort(
          (a, b) =>
            new Date(a.completedAt).getTime() -
            new Date(b.completedAt).getTime()
        );
        break;

      case "rating":
        filtered.sort((a, b) => b.rating - a.rating);
        break;

      case "title":
        filtered.sort((a, b) => a.title.localeCompare(b.title));
        break;
    }

    return filtered.slice(0, maxDisplay);
  }, [books, searchQuery, sortBy, filterBy, maxDisplay]);

  /* -------------------------------- */
  /* Dashboard Stats                  */
  /* -------------------------------- */

  const stats = useMemo(() => {
    const now = new Date(); // Calculate inside the memo
    const totalBooks = books.length;
    const averageRating = books.reduce((sum, b) => sum + b.rating, 0) / (books.length || 1);
    const recentBooks = books.filter((book) => {
      const d = new Date(book.completedAt);
      return (now.getTime() - d.getTime()) / (1000 * 60 * 60 * 24) <= 30;
    }).length;
    const favorites = books.filter((b) => b.rating >= 4).length;

    return {
      totalBooks,
      averageRating,
      recentBooks,
      favorites,
    };
  }, [books]);

  return (
    <div
      className={cn(
        "rounded-2xl border bg-card p-6 shadow-sm transition-all hover:shadow-md",
        className
      )}
    >
      {/* ================= Header ================= */}
      <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Library className="h-5 w-5 text-primary" />
            <h3 className="text-xl font-semibold">
              Reading History
            </h3>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">
            Keep track of every book you&apos;ve completed.
          </p>
        </div>

        <Button variant="ghost">
          <Link href="/library/history">
            View All
            <ChevronRight className="ml-1 h-4 w-4" />
          </Link>
        </Button>
      </div>

      {/* ================= Stats ================= */}
      {showStats && books.length > 0 && (
        <div className="mb-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-xl border bg-gradient-to-br from-primary/10 to-transparent p-4 transition-all hover:shadow-sm">
            <div className="flex items-center justify-between">
              <BookOpen className="h-5 w-5 text-primary" />
              <Badge variant="secondary">Total</Badge>
            </div>
            <p className="mt-4 text-3xl font-bold">
              {stats.totalBooks}
            </p>
            <p className="text-sm text-muted-foreground">
              Books Completed
            </p>
          </div>

          <div className="rounded-xl border bg-gradient-to-br from-yellow-500/10 to-transparent p-4 transition-all hover:shadow-sm">
            <div className="flex items-center justify-between">
              <Star className="h-5 w-5 text-yellow-500 fill-yellow-500" />
              <Badge variant="outline">Rating</Badge>
            </div>
            <p className="mt-4 text-3xl font-bold">
              {stats.averageRating.toFixed(1)}
            </p>
            <p className="text-sm text-muted-foreground">
              Average Rating
            </p>
          </div>

          <div className="rounded-xl border bg-gradient-to-br from-emerald-500/10 to-transparent p-4 transition-all hover:shadow-sm">
            <div className="flex items-center justify-between">
              <TrendingUp className="h-5 w-5 text-emerald-500" />
              <Badge variant="outline">Recent</Badge>
            </div>
            <p className="mt-4 text-3xl font-bold">
              {stats.recentBooks}
            </p>
            <p className="text-sm text-muted-foreground">
              Last 30 Days
            </p>
          </div>

          <div className="rounded-xl border bg-gradient-to-br from-violet-500/10 to-transparent p-4 transition-all hover:shadow-sm">
            <div className="flex items-center justify-between">
              <Award className="h-5 w-5 text-violet-500" />
              <Badge variant="outline">Favorites</Badge>
            </div>
            <p className="mt-4 text-3xl font-bold">
              {stats.favorites}
            </p>
            <p className="text-sm text-muted-foreground">
              Rated 4★ or Higher
            </p>
          </div>
        </div>
      )}

      {/* ================= Search ================= */}
      {showSearch && books.length > 0 && (
        <div className="mb-6 flex flex-col gap-3 lg:flex-row lg:items-center">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search books or authors..."
              className="pl-10"
            />
          </div>

          <div className="flex gap-2">
            <DropdownMenu>
              <DropdownMenuTrigger>
                <Button variant="outline">
                  <ArrowUpDown className="mr-2 h-4 w-4" />
                  Sort
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setSortBy("recent")}>
                  Most Recent
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setSortBy("oldest")}>
                  Oldest
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setSortBy("rating")}>
                  Highest Rated
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setSortBy("title")}>
                  Alphabetical
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <DropdownMenu>
              <DropdownMenuTrigger>
                <Button variant="outline">
                  <Filter className="mr-2 h-4 w-4" />
                  Filter
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setFilterBy("all")}>
                  All Time
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setFilterBy("this-month")}>
                  This Month
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setFilterBy("this-year")}>
                  This Year
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setFilterBy("last-30-days")}>
                  Last 30 Days
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      )}

      {/* ================= Empty State ================= */}
      {books.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed py-16 text-center">
          <div className="mb-5 rounded-full bg-primary/10 p-5">
            <BookOpen className="h-8 w-8 text-primary" />
          </div>
          <h4 className="text-xl font-semibold">
            No reading history yet
          </h4>
          <p className="mt-2 max-w-md text-sm text-muted-foreground">
            Complete your first book to begin building your reading
            history and unlock personalized recommendations.
          </p>
          <Button className="mt-6">
            <Link href="/discover">
              Discover Books
              <ChevronRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      )}

      {/* ================= Search Empty ================= */}
      {books.length > 0 && displayBooks.length === 0 && searchQuery && (
        <div className="rounded-xl border border-dashed py-12 text-center">
          <Search className="mx-auto mb-3 h-8 w-8 text-muted-foreground" />
          <h4 className="font-medium">No books found</h4>
          <p className="mt-2 text-sm text-muted-foreground">
            Try searching with a different title or author.
          </p>
        </div>
      )}

      {/* ================= Reading List ================= */}
      {displayBooks.length > 0 && (
        <div className="space-y-4">
          {displayBooks.map((book) => {
            const now = new Date(); // Calculate fresh for each item
            return (
              <Link
                key={book.id}
                href={`/books/${book.id}`}
                className={cn(
                  "group flex gap-4 rounded-2xl border p-4 transition-all duration-300",
                  "hover:border-primary/20",
                  "hover:bg-muted/30",
                  "hover:shadow-md"
                )}
              >
                {/* Cover */}
                <div className="relative h-24 w-16 shrink-0 overflow-hidden rounded-lg bg-muted">
                  {book.cover ? (
                    <Image
                      src={book.cover}
                      alt={book.title}
                      fill
                      className="object-cover transition-transform duration-300 group-hover:scale-105"
                    />
                  ) : (
                    <div className="flex h-full items-center justify-center">
                      <BookOpen className="h-6 w-6 text-muted-foreground" />
                    </div>
                  )}
                  {book.progress === 100 && (
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-emerald-500" />
                  )}
                </div>

                {/* Main Content */}
                <div className="flex min-w-0 flex-1 flex-col justify-between">
                  <div>
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <h4 className="truncate text-base font-semibold transition-colors group-hover:text-primary">
                          {book.title}
                        </h4>
                        <p className="truncate text-sm text-muted-foreground">
                          {book.author}
                        </p>
                      </div>
                      <Badge variant="secondary" className="shrink-0">
                        Completed
                      </Badge>
                    </div>

                    {/* Metadata */}
                    <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <CalendarDays className="h-3.5 w-3.5" />
                        {formatDate(book.completedAt, now)}
                      </div>

                      <div className="flex items-center gap-1">
                        {renderStars(book.rating)}
                      </div>

                      {book.pagesRead && book.totalPages && (
                        <div className="flex items-center gap-1">
                          <BookOpen className="h-3.5 w-3.5" />
                          {book.pagesRead} / {book.totalPages} pages
                        </div>
                      )}

                      {book.timeSpent && (
                        <div className="flex items-center gap-1">
                          <Clock className="h-3.5 w-3.5" />
                          {book.timeSpent}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Hover Arrow */}
                <div className="hidden items-center sm:flex">
                  <ChevronRight
                    className={cn(
                      "h-5 w-5 text-muted-foreground transition-all duration-300",
                      "opacity-0 -translate-x-2",
                      "group-hover:translate-x-0",
                      "group-hover:opacity-100"
                    )}
                  />
                </div>
              </Link>
            );
          })}
        </div>
      )}

      {/* ================= Footer ================= */}
      {books.length > maxDisplay && displayBooks.length > 0 && (
        <div className="mt-6 flex items-center justify-center border-t pt-5">
          <p className="text-xs text-muted-foreground">
            Showing{" "}
            <span className="font-medium text-foreground">
              {displayBooks.length}
            </span>{" "}
            of{" "}
            <span className="font-medium text-foreground">
              {books.length}
            </span>{" "}
            completed books
          </p>
        </div>
      )}
    </div>
  );
}