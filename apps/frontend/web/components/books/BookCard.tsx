// apps/frontend/web/components/books/BookCard.tsx

"use client";

import Link from "next/link";
import { useState } from "react";
import { Heart } from "lucide-react"; // Add Heart import
import { Badge } from "@/components/ui/badge";
import { Book } from "@/lib/types";
import {
  BookCover,
  BookRating,
  BookActions,
} from "@/components/books";
import { cn } from "@/lib/utils";
import { favoriteService } from "@/lib/services/favorite.service"; // Add this import

// Progress Bar Component
function ProgressBar({ value, className }: { value: number; className?: string }) {
  return (
    <div className={cn("h-1.5 w-full overflow-hidden rounded-full bg-muted", className)}>
      <div
        className="h-full rounded-full bg-gradient-to-r from-primary to-violet-500 transition-all duration-500"
        style={{ width: `${Math.min(Math.max(value, 0), 100)}%` }}
      />
    </div>
  );
}

// Extend the Book type to include optional progress
interface ExtendedBook extends Book {
  progress?: number;
  description?: string;
  coverImage?: string;
  averageRating?: number;  // ✅ Add this
  //rating?: number;   
  ratingsCount?: number;
  isFavorite?: boolean;
  isInLibrary?: boolean;
  genres?: string[];
  authors?: string[];
  
}

interface BookCardProps {
  book: ExtendedBook;
  className?: string;
  href?: string;
  showActions?: boolean;
  showProgress?: boolean;
  showGenres?: boolean;
  showDescription?: boolean;
  priority?: boolean;
  variant?: "default" | "compact" | "horizontal" | "featured";
  size?: "sm" | "md" | "lg";
  onFavorite?: () => void;
  onLibrary?: () => void;
  onView?: () => void;
  onMore?: () => void;
  onQuickView?: () => void;
}

// ✅ THIS IS THE BOOKCARD COMPONENT - Now properly exported!
export function BookCard({
  book,
  className,
  href,
  priority = false,
  showActions = true,
  showProgress = false,
  showGenres = true,
  showDescription = false,
  variant = "default",
  size = "md",
  onFavorite,
  onLibrary,
  onView,
  onMore,
  onQuickView,
}: BookCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  // Local state for favorite
  const [isFavorite, setIsFavorite] = useState(
    book.isFavorite ?? false
  );
  const [saving, setSaving] = useState(false);

  // Toggle favorite function
  const toggleFavorite = async () => {
    if (saving) return;

    try {
      setSaving(true);

      if (isFavorite) {
        await favoriteService.removeFavorite(String(book.id));
        setIsFavorite(false);
      } else {
        await favoriteService.addFavorite(String(book.id));
        setIsFavorite(true);
      }
    } catch (err) {
      console.error("Favorite failed:", err);
    } finally {
      setSaving(false);
    }
  };

  // Safely get authors
  // Get author name from the centralized Book model
const authorString = book.author?.name || "Unknown Author";
  // Safely get genres
  const genres = book.genres || [];

  // Size configurations
  const sizeConfig = {
    sm: {
      coverWidth: 120,
      coverHeight: 170,
      padding: "p-3",
      gap: "gap-2",
      title: "text-sm",
      author: "text-xs",
    },
    md: {
      coverWidth: 180,
      coverHeight: 260,
      padding: "p-4",
      gap: "gap-3",
      title: "text-base",
      author: "text-sm",
    },
    lg: {
      coverWidth: 240,
      coverHeight: 340,
      padding: "p-5",
      gap: "gap-4",
      title: "text-lg",
      author: "text-base",
    },
  };

  const styles = sizeConfig[size];

  // Cover image source.
  //
  // The canonical `Book` type (lib/types/book.ts) exposes `cover`, and
  // mapApiBookToBook() populates `cover`. The default/horizontal/featured
  // variants below previously read `coverImage` ONLY, which nothing ever set,
  // so every card rendered without artwork on discover, library and search.
  // `cover?.` is checked first; `coverImage` remains as a fallback for any
  // caller that still passes the legacy field.
  const coverSrc = book.cover ?? book.coverImage ?? undefined;

  // Rating source. Same class of bug as the cover above: the canonical Book
  // type and the API adapter set `rating`, while these variants read
  // `averageRating`, so every card showed a 0-star rating. Prefer the
  // canonical field and keep the legacy one as a fallback.
  const ratingValue = book.rating ?? book.averageRating ?? 0;
  const ratingCount = book.ratingsCount ?? undefined;

  // Compact variant
  if (variant === "compact") {
    return (
      <div
        className={cn(
          "group flex gap-4 rounded-xl border border-border/50 bg-card p-3 transition-all duration-300 hover:shadow-md",
          className
        )}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <Link href={href || "#"} className="shrink-0">
          <BookCover
            src={book.cover ?? undefined}
            alt={book.title}
            width={80}
            height={110}
            priority={priority}
            className="rounded-lg"
          />
        </Link>
        <div className="flex flex-1 flex-col justify-between min-w-0">
          <div>
            <Link href={href || "#"}>
              <h4 className="font-medium line-clamp-1 hover:text-primary transition-colors">
                {book.title}
              </h4>
            </Link>
            <p className="text-sm text-muted-foreground line-clamp-1">
              {authorString}
            </p>
            <BookRating
              rating={book.rating ?? 0}
              ratingsCount={book.ratingsCount}
              size="sm"
              showStars={false}
            />
          </div>
          {showActions && (
            <div className="flex gap-1 mt-2">
              <BookActions
                isFavorite={isFavorite}
                isInLibrary={book.isInLibrary}
                onFavorite={onFavorite ?? toggleFavorite}
                onLibrary={onLibrary}
                onView={onView}
                onMore={onMore}
              />
            </div>
          )}
        </div>
      </div>
    );
  }

  // Horizontal variant
  if (variant === "horizontal") {
    return (
      <div
        className={cn(
          "group flex gap-6 rounded-2xl border border-border/50 bg-card p-4 transition-all duration-300 hover:shadow-md",
          className
        )}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <Link href={href || "#"} className="shrink-0">
          <BookCover
            src={coverSrc}
            alt={book.title}
            width={styles.coverWidth}
            height={styles.coverHeight}
            priority={priority}
            className="rounded-xl"
          />
        </Link>
        <div className="flex flex-1 flex-col justify-between py-1 min-w-0">
          <div className="space-y-2">
            <Link href={href || "#"}>
              <h3 className={cn("font-semibold line-clamp-2 hover:text-primary transition-colors", styles.title)}>
                {book.title}
              </h3>
            </Link>
            <p className={cn("text-muted-foreground", styles.author)}>
              {authorString}
            </p>
            
            <BookRating
              rating={ratingValue}
              ratingsCount={ratingCount}
              size={size === "sm" ? "sm" : size === "lg" ? "lg" : "md"}
              showStars={true}
            />

            {showDescription && book.description && (
              <p className="text-sm text-muted-foreground line-clamp-3">
                {book.description}
              </p>
            )}

            {showGenres && genres.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {genres.slice(0, 3).map((genre) => (
                  <Badge key={genre} variant="secondary" className="text-xs">
                    {genre}
                  </Badge>
                ))}
                {genres.length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{genres.length - 3}
                  </Badge>
                )}
              </div>
            )}

            {showProgress && book.progress !== undefined && (
              <div className="space-y-1">
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Reading Progress</span>
                  <span>{book.progress}%</span>
                </div>
                <ProgressBar value={book.progress} className="h-1.5" />
              </div>
            )}
          </div>

          {showActions && (
            <div className="flex items-center gap-2 pt-3 border-t border-border/30">
              <BookActions
                isFavorite={isFavorite}
                isInLibrary={book.isInLibrary}
                onFavorite={onFavorite ?? toggleFavorite}
                onLibrary={onLibrary}
                onView={onView}
                onMore={onMore}
              />
            </div>
          )}
        </div>
      </div>
    );
  }

  // Featured variant
  if (variant === "featured") {
    return (
      <div
        className={cn(
          "group relative overflow-hidden rounded-2xl border border-border/50 bg-card transition-all duration-300 hover:shadow-xl",
          className
        )}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <div className="flex flex-col md:flex-row">
          <Link href={href || "#"} className="md:shrink-0">
            <BookCover
              src={coverSrc}
              alt={book.title}
              width={styles.coverWidth}
              height={styles.coverHeight}
              priority={priority}
              className="rounded-t-2xl md:rounded-l-2xl md:rounded-r-none"
            />
          </Link>
          <div className="flex-1 space-y-3 p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <Link href={href || "#"}>
                  <h3 className="text-xl font-bold hover:text-primary transition-colors line-clamp-2">
                    {book.title}
                  </h3>
                </Link>
                <p className="text-muted-foreground">
                  {authorString}
                </p>
              </div>
              {isFavorite && (
                <Badge variant="default" className="shrink-0">
                  ★ Favorite
                </Badge>
              )}
            </div>

            <BookRating
              rating={ratingValue}
              ratingsCount={ratingCount}
              size="lg"
              showStars={true}
            />

            {showDescription && book.description && (
              <p className="text-sm text-muted-foreground line-clamp-3">
                {book.description}
              </p>
            )}

            {showGenres && genres.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {genres.slice(0, 4).map((genre) => (
                  <Badge key={genre} variant="secondary">
                    {genre}
                  </Badge>
                ))}
                {genres.length > 4 && (
                  <Badge variant="outline">
                    +{genres.length - 4}
                  </Badge>
                )}
              </div>
            )}

            {showActions && (
              <div className="flex items-center gap-2 pt-2 border-t border-border/30">
                <BookActions
                  isFavorite={isFavorite}
                  isInLibrary={book.isInLibrary}
                  onFavorite={onFavorite ?? toggleFavorite}
                  onLibrary={onLibrary}
                  onView={onView}
                  onMore={onMore}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Default variant
  const content = (
    <div
      className={cn(
        "group overflow-hidden rounded-2xl border border-border/50 bg-card",
        "transition-all duration-300",
        "hover:-translate-y-1 hover:shadow-xl hover:border-primary/20",
        className
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="relative">
        <Link href={href || "#"} className="block relative">
          <BookCover
            src={coverSrc}
            alt={book.title}
            width={styles.coverWidth}
            height={styles.coverHeight}
            priority={priority}
            className="w-full rounded-t-2xl"
          />
          {onQuickView && isHovered && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <span className="text-white text-sm font-medium bg-black/50 px-4 py-2 rounded-full">
                Quick View
              </span>
            </div>
          )}
        </Link>

        {/* Favorite button - replaced with new implementation */}
        <button
          onClick={toggleFavorite}
          disabled={saving}
          className="absolute right-3 top-3 rounded-full bg-white/90 p-2 shadow transition hover:scale-105 disabled:opacity-50"
          aria-label={isFavorite ? "Remove from favorites" : "Add to favorites"}
        >
          <Heart
            className={`h-5 w-5 ${
              isFavorite
                ? "fill-red-500 text-red-500"
                : "text-gray-500"
            }`}
          />
        </button>
      </div>

      <div className={cn("space-y-2.5", styles.padding)}>
        <div>
          <Link href={href || "#"}>
            <h3 className={cn(
              "font-semibold line-clamp-2 hover:text-primary transition-colors",
              styles.title
            )}>
              {book.title}
            </h3>
          </Link>
          <p className={cn("text-muted-foreground line-clamp-1", styles.author)}>
            {authorString}
          </p>
        </div>

        <BookRating
          rating={ratingValue}
          ratingsCount={ratingCount}
          size={size === "sm" ? "sm" : size === "lg" ? "lg" : "md"}
          showStars={size !== "sm"}
        />

        {showGenres && genres.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {genres.slice(0, size === "sm" ? 1 : 2).map((genre) => (
              <Badge key={genre} variant="secondary" className="text-[10px] px-2 py-0">
                {genre}
              </Badge>
            ))}
            {genres.length > (size === "sm" ? 1 : 2) && (
              <Badge variant="outline" className="text-[10px] px-2 py-0">
                +{genres.length - (size === "sm" ? 1 : 2)}
              </Badge>
            )}
          </div>
        )}

        {showProgress && book.progress !== undefined && (
          <div className="space-y-1">
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Progress</span>
              <span>{book.progress}%</span>
            </div>
            <ProgressBar value={book.progress} className="h-1" />
          </div>
        )}

        {showActions && (
          <div className={cn(
            "flex items-center justify-between pt-2 border-t border-border/30",
            size === "sm" ? "gap-1" : "gap-2"
          )}>
            <BookActions
              isFavorite={isFavorite}
              isInLibrary={book.isInLibrary}
              onFavorite={onFavorite ?? toggleFavorite}
              onLibrary={onLibrary}
              onView={onView}
              onMore={onMore}
            />
          </div>
        )}
      </div>
    </div>
  );

  if (!href) return content;
  return content;
}

// Export the types as well
export type { BookCardProps, ExtendedBook };