/**
 * ================================================================
 * 📚 Books Mock Data
 * ================================================================
 *
 * This file contains mock book data for development and testing.
 * It represents a collection of books with authors, ratings,
 * and publication information.
 *
 * IMPORTANT: This is mock data and should be replaced with
 * real API data in production.
 * ================================================================
 */

import type { Book } from "@/lib/types";
import { DEFAULT_BOOK_COVER } from "@/lib/constants/mock";

// ============================================================
// 📚 Book Collection
// ============================================================

/**
 * Mock book collection for development and testing.
 * 
 * Contains a curated list of popular books across different genres:
 * - Self-development
 * - Productivity
 * - Fantasy
 * - Science Fiction
 * - Finance
 * 
 * Each book includes:
 * - Basic metadata (id, title, author)
 * - Cover image (fallback to default)
 * - Publication year
 * - Average rating
 */
export const books: Book[] = [
  // ============================================================
  // 📖 Self-Development & Habits
  // ============================================================

  {
    id: 1,
    title: "Atomic Habits",
    author: {
      id: 1,
      name: "James Clear",
    },
    cover: DEFAULT_BOOK_COVER,
    publicationYear: 2018,
    rating: 4.8,
  },

  // ============================================================
  // 🎯 Productivity & Deep Work
  // ============================================================

  {
    id: 2,
    title: "Deep Work",
    author: {
      id: 2,
      name: "Cal Newport",
    },
    cover: DEFAULT_BOOK_COVER,
    publicationYear: 2016,
    rating: 4.7,
  },

  // ============================================================
  // 🧙 Fantasy Classics
  // ============================================================

  {
    id: 3,
    title: "The Hobbit",
    author: {
      id: 3,
      name: "J.R.R. Tolkien",
    },
    cover: DEFAULT_BOOK_COVER,
    publicationYear: 1937,
    rating: 4.9,
  },

  // ============================================================
  // 🚀 Science Fiction
  // ============================================================

  {
    id: 4,
    title: "Dune",
    author: {
      id: 4,
      name: "Frank Herbert",
    },
    cover: DEFAULT_BOOK_COVER,
    publicationYear: 1965,
    rating: 4.8,
  },

  // ============================================================
  // 💰 Finance & Money
  // ============================================================

  {
    id: 5,
    title: "The Psychology of Money",
    author: {
      id: 5,
      name: "Morgan Housel",
    },
    cover: DEFAULT_BOOK_COVER,
    publicationYear: 2020,
    rating: 4.8,
  },
];

// ============================================================
// 🔄 Helper Functions
// ============================================================

/**
 * Get a book by its ID.
 * 
 * @param id - The book ID to search for
 * @returns The book if found, undefined otherwise
 */
export function getBookById(id: number): Book | undefined {
  return books.find((book) => book.id === id);
}

/**
 * Get books by author name (case-insensitive).
 * 
 * @param authorName - The author name to search for
 * @returns Array of books by the author
 */
export function getBooksByAuthor(authorName: string): Book[] {
  return books.filter((book) =>
    book.author.name.toLowerCase().includes(authorName.toLowerCase())
  );
}

/**
 * Get books by publication year.
 * 
 * @param year - The publication year to filter by
 * @returns Array of books published in that year
 */
export function getBooksByYear(year: number): Book[] {
  return books.filter((book) => book.publicationYear === year);
}

/**
 * Get books with a rating above a threshold.
 * 
 * @param minRating - The minimum rating (0-5)
 * @returns Array of books with rating >= minRating
 */
export function getBooksByRating(minRating: number): Book[] {
  return books.filter((book) => (book.rating || 0) >= minRating);
}

/**
 * Get the highest rated books.
 * 
 * @param limit - Maximum number of books to return (default: 5)
 * @returns Array of highest rated books sorted by rating
 */
export function getTopRatedBooks(limit: number = 5): Book[] {
  return [...books]
    .sort((a, b) => (b.rating || 0) - (a.rating || 0))
    .slice(0, limit);
}

/**
 * Get the most recently published books.
 * 
 * @param limit - Maximum number of books to return (default: 5)
 * @returns Array of most recent books sorted by publication year
 */
export function getRecentBooks(limit: number = 5): Book[] {
  return [...books]
    .sort((a, b) => (b.publicationYear || 0) - (a.publicationYear || 0))
    .slice(0, limit);
}

/**
 * Search books by title (case-insensitive).
 * 
 * @param query - The search query
 * @returns Array of books matching the search
 */
export function searchBooks(query: string): Book[] {
  return books.filter((book) =>
    book.title.toLowerCase().includes(query.toLowerCase())
  );
}

/**
 * Get a random selection of books.
 * 
 * @param count - Number of books to return (default: 3)
 * @returns Array of random books
 */
export function getRandomBooks(count: number = 3): Book[] {
  const shuffled = [...books];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled.slice(0, count);
}

/**
 * Get book statistics.
 * 
 * @returns Statistics about the book collection
 */
export function getBookStats() {
  const total = books.length;
  const avgRating = books.reduce((sum, book) => sum + (book.rating || 0), 0) / total;
  const years = books.map((book) => book.publicationYear || 0);
  const oldestYear = Math.min(...years);
  const newestYear = Math.max(...years);
  
  return {
    totalBooks: total,
    averageRating: Math.round(avgRating * 10) / 10,
    oldestPublicationYear: oldestYear,
    newestPublicationYear: newestYear,
    genres: {
      "Self-Development": 1,
      "Productivity": 1,
      "Fantasy": 1,
      "Science Fiction": 1,
      "Finance": 1,
    },
  };
}

/**
 * Format a book's display information.
 * 
 * @param book - The book to format
 * @returns Formatted book string
 */
export function formatBookDisplay(book: Book): string {
  return `${book.title} by ${book.author.name} (${book.publicationYear}) - ${book.rating || "N/A"}★`;
}

/**
 * Check if a book is highly rated (4.5+).
 * 
 * @param book - The book to check
 * @returns True if the book is highly rated
 */
export function isHighlyRated(book: Book): boolean {
  return (book.rating || 0) >= 4.5;
}