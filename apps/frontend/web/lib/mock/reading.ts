/**
 * ================================================================
 * 📖 Reading Mock Data
 * ================================================================
 *
 * This file contains mock reading data for development and testing.
 * It represents:
 * - Books currently being read (Continue Reading)
 * - Recently viewed books
 * - Reading history
 * - Reading goals and statistics
 *
 * IMPORTANT: This is mock data and should be replaced with
 * real API data in production.
 * ================================================================
 */

import type {
  ContinueReadingBook,
  RecentlyViewedBook,
  ReadingHistoryItem,
  ReadingGoal,
  ReadingProgress,
} from "@/lib/types";
// FIX: Removed unused imports
import { DEFAULT_BOOK_COVER } from "@/lib/constants/mock";

// ============================================================
// 📊 Reading Progress Factory
// ============================================================

/**
 * Create a reading progress object.
 */
function createProgress(
  currentPage: number,
  totalPages: number,
  lastReadAt?: string
): ReadingProgress {
  const percentage = Math.min(Math.round((currentPage / totalPages) * 100), 100);
  return {
    percentage,
    currentPage,
    totalPages,
    lastReadAt: lastReadAt || new Date().toISOString(),
  };
}

// ============================================================
// 📚 Continue Reading
// ============================================================

/**
 * Mock books currently being read by the user.
 * Used in the "Continue Reading" section of the dashboard.
 */
export const continueReadingBooks: ContinueReadingBook[] = [
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
    progress: createProgress(142, 320, "2026-07-18T14:30:00Z"),
    estimatedTimeLeft: 120,
    timeLeftDisplay: "2 hours",
  },
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
    progress: createProgress(78, 304, "2026-07-17T20:15:00Z"),
    estimatedTimeLeft: 90,
    timeLeftDisplay: "1.5 hours",
  },
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
    progress: createProgress(210, 310, "2026-07-16T10:00:00Z"),
    estimatedTimeLeft: 45,
    timeLeftDisplay: "45 minutes",
  },
];

// ============================================================
// 👀 Recently Viewed
// ============================================================

/**
 * Mock recently viewed books.
 * Used in the "Recently Viewed" section of the dashboard.
 */
export const recentlyViewedBooks: RecentlyViewedBook[] = [
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
    viewedAt: "2026-07-18T12:30:00Z",
    viewedAtDisplay: "2 hours ago",
  },
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
    viewedAt: "2026-07-17T09:15:00Z",
    viewedAtDisplay: "Yesterday",
  },
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
    viewedAt: "2026-07-16T16:45:00Z",
    viewedAtDisplay: "2 days ago",
  },
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
    viewedAt: "2026-07-15T11:20:00Z",
    viewedAtDisplay: "3 days ago",
  },
];

// ============================================================
// 📜 Reading History
// ============================================================

/**
 * Mock reading history entries.
 * Used in the reading history page and profile.
 */
export const readingHistory: ReadingHistoryItem[] = [
  {
    id: 1,
    book: {
      id: 6,
      title: "The 7 Habits of Highly Effective People",
      author: {
        id: 6,
        name: "Stephen R. Covey",
      },
      cover: DEFAULT_BOOK_COVER,
      publicationYear: 1989,
      rating: 4.6,
    },
    startedAt: "2026-06-01T08:00:00Z",
    completedAt: "2026-06-28T10:30:00Z",
    progress: createProgress(381, 381, "2026-06-28T10:30:00Z"),
    startedAtDisplay: "June 1, 2026",
    completedAtDisplay: "June 28, 2026",
    isCompleted: true,
    readingDuration: 540, // 9 hours
  },
  {
    id: 2,
    book: {
      id: 7,
      title: "The Alchemist",
      author: {
        id: 7,
        name: "Paulo Coelho",
      },
      cover: DEFAULT_BOOK_COVER,
      publicationYear: 1988,
      rating: 4.5,
    },
    startedAt: "2026-05-15T09:00:00Z",
    completedAt: "2026-05-30T14:20:00Z",
    progress: createProgress(208, 208, "2026-05-30T14:20:00Z"),
    startedAtDisplay: "May 15, 2026",
    completedAtDisplay: "May 30, 2026",
    isCompleted: true,
    readingDuration: 420, // 7 hours
  },
  {
    id: 3,
    book: {
      id: 8,
      title: "Thinking, Fast and Slow",
      author: {
        id: 8,
        name: "Daniel Kahneman",
      },
      cover: DEFAULT_BOOK_COVER,
      publicationYear: 2011,
      rating: 4.7,
    },
    startedAt: "2026-04-10T10:00:00Z",
    completedAt: "2026-05-05T16:45:00Z",
    progress: createProgress(499, 499, "2026-05-05T16:45:00Z"),
    startedAtDisplay: "April 10, 2026",
    completedAtDisplay: "May 5, 2026",
    isCompleted: true,
    readingDuration: 960, // 16 hours
  },
  {
    id: 4,
    book: {
      id: 9,
      title: "Sapiens",
      author: {
        id: 9,
        name: "Yuval Noah Harari",
      },
      cover: DEFAULT_BOOK_COVER,
      publicationYear: 2011,
      rating: 4.6,
    },
    startedAt: "2026-03-01T08:00:00Z",
    progress: createProgress(250, 512, "2026-07-10T14:30:00Z"),
    startedAtDisplay: "March 1, 2026",
    isCompleted: false,
  },
];

// ============================================================
// 🎯 Reading Goals
// ============================================================

/**
 * Mock reading goals.
 * Used in the dashboard and reading goal section.
 */
export const readingGoals: ReadingGoal[] = [
  {
    goalType: "books",
    target: 52,
    current: 48,
    currentStreak: 14,
    longestStreak: 45,
    progressPercentage: 92,
    progressDisplay: "48 / 52 books",
    status: "on-track",
    deadline: "2026-12-31T23:59:59Z",
    booksPerWeek: 1.2,
  },
];

// ============================================================
// 🔄 Helper Functions
// ============================================================

/**
 * Get continue reading books for a user.
 */
export function getContinueReadingBooks(): ContinueReadingBook[] {
  return continueReadingBooks;
}

/**
 * Get recently viewed books for a user.
 */
export function getRecentlyViewedBooks(): RecentlyViewedBook[] {
  return recentlyViewedBooks;
}

/**
 * Get reading history for a user.
 */
export function getReadingHistory(): ReadingHistoryItem[] {
  return readingHistory;
}

/**
 * Get reading goals for a user.
 */
export function getReadingGoals(): ReadingGoal[] {
  return readingGoals;
}

/**
 * Get the primary reading goal (first one).
 */
export function getPrimaryReadingGoal(): ReadingGoal | undefined {
  return readingGoals[0];
}

/**
 * Get books that are currently in progress (not completed).
 */
export function getInProgressBooks(): ContinueReadingBook[] {
  return continueReadingBooks.filter(
    (book) => book.progress.percentage > 0 && book.progress.percentage < 100
  );
}

/**
 * Get books that are completed.
 */
export function getCompletedBooks(): ContinueReadingBook[] {
  return continueReadingBooks.filter(
    (book) => book.progress.percentage >= 100
  );
}

/**
 * Get the total number of pages read across all books.
 */
export function getTotalPagesRead(): number {
  return continueReadingBooks.reduce(
    (total, book) => total + book.progress.currentPage,
    0
  );
}

/**
 * Get the average progress percentage across all books.
 */
export function getAverageProgress(): number {
  if (continueReadingBooks.length === 0) return 0;
  const total = continueReadingBooks.reduce(
    (sum, book) => sum + book.progress.percentage,
    0
  );
  return Math.round(total / continueReadingBooks.length);
}

/**
 * Get the most recently viewed book.
 */
export function getMostRecentView(): RecentlyViewedBook | undefined {
  if (recentlyViewedBooks.length === 0) return undefined;
  return [...recentlyViewedBooks].sort(
    (a, b) => new Date(b.viewedAt).getTime() - new Date(a.viewedAt).getTime()
  )[0];
}

/**
 * Get reading history by year.
 */
export function getReadingHistoryByYear(year: number): ReadingHistoryItem[] {
  return readingHistory.filter((item) => {
    const date = new Date(item.startedAt);
    return date.getFullYear() === year;
  });
}

/**
 * Get completed reading history items.
 */
export function getCompletedHistoryItems(): ReadingHistoryItem[] {
  return readingHistory.filter((item) => item.isCompleted);
}

/**
 * Get reading statistics summary.
 */
export function getReadingStats() {
  const totalBooks = continueReadingBooks.length + readingHistory.length;
  const completedBooks = readingHistory.filter((item) => item.isCompleted).length;
  const inProgressBooks = continueReadingBooks.filter(
    (book) => book.progress.percentage > 0 && book.progress.percentage < 100
  ).length;
  const totalPagesRead = readingHistory.reduce(
    (total, item) => total + item.progress.totalPages,
    0
  );

  return {
    totalBooks,
    completedBooks,
    inProgressBooks,
    totalPagesRead,
    averageRating: 4.7,
    longestStreak: 45,
    currentStreak: 14,
  };
}