// lib/types/book.ts

/**
 * ================================================================
 * 📚 Book Domain Models
 * ================================================================
 *
 * These interfaces define the frontend representation of books.
 * They are UI domain models, NOT database models.
 *
 * Every feature that displays books should build on these interfaces.
 * ================================================================
 */

// ✅ Import from common
// FIX: Removed unused 'ISODateString' import
import type { ID, Timestamp, Maybe } from "./common";

// ============================================================
// 👤 Author
// ============================================================

/**
 * Basic author information.
 * Used across all book-related features.
 */
export interface Author {
  /** Unique identifier for the author */
  id: ID | string;

  /** Author's full name */
  name: string;

  /** URL to author's profile image (optional) */
  avatar?: Maybe<string>;

  /** Short biography of the author (optional) */
  biography?: Maybe<string>;
}

// ============================================================
// 📊 Book Statistics
// ============================================================

/**
 * Reading statistics for a book.
 * Used for displaying metrics on book cards and detail pages.
 */
export interface BookStats {
  /** Average rating out of 5 (0-5) */
  averageRating?: Maybe<number>;

  /** Total number of ratings received */
  ratingsCount?: Maybe<number>;

  /** Total number of pages in the book */
  pages?: Maybe<number>;

  /** Number of times the book has been viewed */
  views?: Maybe<number>;

  /** Number of times the book has been favorited */
  favorites?: Maybe<number>;
}

// ============================================================
// 📖 Book Models
// ============================================================

/**
 * Base Book model.
 * 
 * The smallest representation of a book used wherever only
 * basic information is required (e.g., lists, cards, search).
 */
export interface Book {
  /** Unique identifier for the book */
  id: ID | string;

  /** Book title */
  title: string;

  /** Book author (minimal info) */
  author: Author;

  /** URL to the book's cover image */
  cover?: Maybe<string>;

  /** Year the book was published */
  publicationYear?: Maybe<number>;

  /** Average rating for the book (0-5) */
  rating?: Maybe<number>;
}

// ============================================================
// 🔍 Search Result Book
// ============================================================

/**
 * Book displayed in search results.
 * 
 * Extends the base Book with search-specific metadata
 * such as highlighted matches.
 */
export interface SearchResultBook extends Book {
  /** Text snippet showing the matched search term */
  matchedText?: Maybe<string>;

  /** Search relevance score */
  relevanceScore?: Maybe<number>;
}

// ============================================================
// 💡 Recommendation Book
// ============================================================

/**
 * Book displayed inside recommendation sections.
 * 
 * Extends the base Book with recommendation-specific data
 * like relevance scores and reasons.
 */
export interface RecommendationBook extends Book {
  /** Recommendation confidence score (0-1) */
  score?: Maybe<number>;

  /** Human-readable reason for the recommendation */
  reason?: Maybe<string>;

  /** Recommendation source */
  source?: Maybe<"similar" | "popular" | "collaborative" | "trending">;
}

// ============================================================
// 📚 Library Book
// ============================================================

/**
 * Book displayed inside the user's personal library.
 * 
 * Extends the base Book with user-specific metadata
 * like favorites, completion status, and reading progress.
 */
export interface LibraryBook extends Book {
  /** Date the book was added to the library */
  dateAdded?: Maybe<Timestamp>;

  /** Whether the book is marked as favorite */
  isFavorite?: Maybe<boolean>;

  /** Whether the book has been completed */
  isCompleted?: Maybe<boolean>;

  /** Reading progress (0-100) */
  progress?: Maybe<number>;

  /** Date the book was last read */
  lastReadAt?: Maybe<Timestamp>;
}

// ============================================================
// 📝 Book Details
// ============================================================

/**
 * Complete book information.
 * 
 * Used on the Book Details page.
 * Extends the base Book with comprehensive metadata.
 */
export interface BookDetails extends Book {
  /** Full book description or synopsis */
  description?: Maybe<string>;

  /** International Standard Book Number (10 or 13 digits) */
  isbn?: Maybe<string>;

  /** Publisher name */
  publisher?: Maybe<string>;

  /** Primary language of the book */
  language?: Maybe<string>;

  /** List of genres the book belongs to */
  genres?: Maybe<string[]>;

  /** Extended statistics for the book */
  stats?: Maybe<BookStats>;

  /** Number of pages */
  pages?: Maybe<number>;
}

// ============================================================
// 🎯 Type Guards
// ============================================================

/**
 * Type guard to check if a book has complete details.
 */
export function isBookDetails(book: Book): book is BookDetails {
  return (book as BookDetails).description !== undefined;
}

/**
 * Type guard to check if a book is a library book.
 */
export function isLibraryBook(book: Book): book is LibraryBook {
  return (book as LibraryBook).dateAdded !== undefined;
}

/**
 * Type guard to check if a book is a recommendation.
 */
export function isRecommendationBook(book: Book): book is RecommendationBook {
  return (book as RecommendationBook).score !== undefined;
}

// ============================================================
// 🏗️ Factory Functions
// ============================================================

/**
 * Create a minimal book object.
 */
export function createBook(params: {
  id: ID | string;
  title: string;
  author: Author;
  cover?: Maybe<string>;
  publicationYear?: Maybe<number>;
  rating?: Maybe<number>;
}): Book {
  return {
    id: params.id,
    title: params.title,
    author: params.author,
    cover: params.cover,
    publicationYear: params.publicationYear,
    rating: params.rating,
  };
}

/**
 * Create a library book from a base book.
 */
export function toLibraryBook(
  book: Book,
  options: {
    isFavorite?: Maybe<boolean>;
    isCompleted?: Maybe<boolean>;
    progress?: Maybe<number>;
  }
): LibraryBook {
  return {
    ...book,
    dateAdded: new Date().toISOString(),
    isFavorite: options.isFavorite || false,
    isCompleted: options.isCompleted || false,
    progress: options.progress || 0,
  };
}

/**
 * Create a recommendation book from a base book.
 */
export function toRecommendationBook(
  book: Book,
  options: {
    score?: Maybe<number>;
    reason?: Maybe<string>;
    source?: Maybe<"similar" | "popular" | "collaborative" | "trending">;
  }
): RecommendationBook {
  return {
    ...book,
    score: options.score || 0,
    reason: options.reason,
    source: options.source || "similar",
  };
}

// ============================================================
// 🔄 Helper Functions
// ============================================================

/**
 * Format a book's author name for display.
 */
export function formatAuthorName(book: Book): string {
  return book.author.name || "Unknown Author";
}

/**
 * Format a book's title for display (capitalize, truncate, etc.).
 */
export function formatBookTitle(book: Book, maxLength?: Maybe<number>): string {
  const title = book.title.trim() || "Untitled";
  if (maxLength && title.length > maxLength) {
    return title.slice(0, maxLength) + "...";
  }
  return title;
}

/**
 * Get a book's display rating or fallback.
 */
export function getBookDisplayRating(book: Book): string {
  const rating = book.rating ?? 0;
  return rating > 0 ? rating.toFixed(1) : "N/A";
}

/**
 * Check if a book has a cover image.
 */
export function hasCover(book: Book): boolean {
  return !!book.cover && book.cover.length > 0;
}

/**
 * Get the year from a date string.
 */
export function getYearFromDate(date?: Maybe<string>): Maybe<number> {
  if (!date) return undefined;
  try {
    return new Date(date).getFullYear();
  } catch {
    return undefined;
  }
}