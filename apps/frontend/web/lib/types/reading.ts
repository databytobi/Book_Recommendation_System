// lib/types/reading.ts

/**
 * ================================================================
 * 📖 Reading Types
 * ================================================================
 *
 * These types define the reading-related data structures for the frontend.
 * They handle:
 * - Reading progress tracking
 * - Continue reading functionality
 * - Recently viewed books
 * - Reading history
 * - Reading goals and streaks
 * ================================================================
 */

import { Book } from "./book";
import type { ISODateString } from "./common";

// ============================================================
// 📊 Reading Progress
// ============================================================

/**
 * Reading progress for a book.
 * 
 * Tracks the user's progress through a book including
 * page numbers, percentage, and last read timestamp.
 */
export interface ReadingProgress {
  /** Percentage of the book completed (0-100) */
  percentage: number;

  /** Current page number the user is on */
  currentPage: number;

  /** Total number of pages in the book */
  totalPages: number;

  /** ISO timestamp of when the book was last read */
  lastReadAt: ISODateString;
}

// ============================================================
// 📚 Continue Reading
// ============================================================

/**
 * Book currently being read.
 * 
 * Extends the base Book with reading progress information.
 * Used in the "Continue Reading" section of the dashboard.
 */
export interface ContinueReadingBook extends Book {
  /** Reading progress for this book */
  progress: ReadingProgress;

  /** Estimated time left to finish (in minutes) */
  estimatedTimeLeft?: number;

  /** Human-readable time left (e.g., "2 hours", "45 minutes") */
  timeLeftDisplay?: string;
}

// ============================================================
// 👀 Recently Viewed
// ============================================================

/**
 * Book recently viewed.
 * 
 * Extends the base Book with a timestamp of when it was viewed.
 * Used in the "Recently Viewed" section of the dashboard.
 */
export interface RecentlyViewedBook extends Book {
  /** ISO timestamp of when the book was viewed */
  viewedAt: ISODateString;

  /** Display-friendly time (e.g., "2 hours ago", "Today") */
  viewedAtDisplay?: string;
}

// ============================================================
// 📜 Reading History
// ============================================================

/**
 * Reading history entry.
 * 
 * Represents a book that has been started or completed by the user.
 * Used in the reading history page and profile.
 */
export interface ReadingHistoryItem {
  /** Unique identifier for the history entry */
  id: number;

  /** The book being read */
  book: Book;

  /** ISO timestamp of when reading started */
  startedAt: ISODateString;

  /** ISO timestamp of when reading was completed (optional) */
  completedAt?: ISODateString;

  /** Reading progress for this entry */
  progress: ReadingProgress;

  /** Display-friendly start date */
  startedAtDisplay?: string;

  /** Display-friendly completion date */
  completedAtDisplay?: string;

  /** Whether the book has been completed */
  isCompleted?: boolean;

  /** Reading duration in minutes */
  readingDuration?: number;
}

// ============================================================
// 🎯 Reading Goals
// ============================================================

/**
 * Supported reading goal types.
 * 
 * - `"books"` - Number of books to read
 * - `"pages"` - Number of pages to read
 * - `"minutes"` - Number of minutes to read
 */
export type ReadingGoalType =
  | "books"
  | "pages"
  | "minutes";

/**
 * Reading goal.
 * 
 * Represents the user's reading goal including target,
 * current progress, and streak information.
 */
export interface ReadingGoal {
  /** The type of goal (books, pages, or minutes) */
  goalType: ReadingGoalType;

  /** The target number to achieve */
  target: number;

  /** Current progress towards the target */
  current: number;

  /** Current reading streak in days */
  currentStreak: number;

  /** Longest streak achieved in days */
  longestStreak: number;

  /** Percentage completed (0-100) */
  progressPercentage: number;

  /** Formatted progress display (e.g., "75 / 100 books") */
  progressDisplay?: string;

  /** Status of the goal (e.g., "On track", "Completed", "Behind") */
  status?: "on-track" | "ahead" | "behind" | "completed";

  /** Deadline for the goal (optional) */
  deadline?: ISODateString;

  /** Books per week needed to reach the goal */
  booksPerWeek?: number;
}

// ============================================================
// 🏗️ Factory Functions
// ============================================================

/**
 * Create reading progress from page numbers.
 */
export function createReadingProgress(params: {
  currentPage: number;
  totalPages: number;
  lastReadAt?: ISODateString;
}): ReadingProgress {
  const percentage = params.totalPages > 0
    ? Math.min(Math.round((params.currentPage / params.totalPages) * 100), 100)
    : 0;

  return {
    percentage,
    currentPage: params.currentPage,
    totalPages: params.totalPages,
    lastReadAt: params.lastReadAt || new Date().toISOString(),
  };
}

/**
 * Create a continue reading book from a book and progress.
 */
export function createContinueReadingBook(params: {
  book: Book;
  currentPage: number;
  totalPages: number;
  lastReadAt?: ISODateString;
}): ContinueReadingBook {
  return {
    ...params.book,
    progress: createReadingProgress({
      currentPage: params.currentPage,
      totalPages: params.totalPages,
      lastReadAt: params.lastReadAt,
    }),
  };
}

/**
 * Create a reading goal with default values.
 */
export function createReadingGoal(params: {
  goalType: ReadingGoalType;
  target: number;
  current?: number;
  currentStreak?: number;
  longestStreak?: number;
}): ReadingGoal {
  const current = params.current || 0;
  const target = params.target;
  const progressPercentage = target > 0 ? Math.min(Math.round((current / target) * 100), 100) : 0;

  return {
    goalType: params.goalType,
    target,
    current,
    currentStreak: params.currentStreak || 0,
    longestStreak: params.longestStreak || 0,
    progressPercentage,
  };
}

// ============================================================
// 🔄 Helper Functions
// ============================================================

/**
 * Type guard to check if a book is a ContinueReadingBook.
 */
export function isContinueReadingBook(book: unknown): book is ContinueReadingBook {
  return book !== null && typeof book === 'object' && 'progress' in book;
}

/**
 * Type guard to check if an item is a ReadingHistoryItem.
 */
export function isReadingHistoryItem(item: unknown): item is ReadingHistoryItem {
  return item !== null && typeof item === 'object' && 'id' in item && 'book' in item && 'progress' in item;
}

/**
 * Check if a book is completed.
 * Works with both ContinueReadingBook and ReadingHistoryItem.
 */
export function isBookCompleted(
  book: ContinueReadingBook | ReadingHistoryItem
): boolean {
  return book.progress.percentage >= 100;
}

/**
 * Check if a book is in progress (started but not completed).
 */
export function isBookInProgress(
  book: ContinueReadingBook | ReadingHistoryItem
): boolean {
  return book.progress.percentage > 0 && book.progress.percentage < 100;
}

/**
 * Check if a book is not started yet.
 */
export function isBookNotStarted(
  book: ContinueReadingBook | ReadingHistoryItem
): boolean {
  return book.progress.percentage === 0;
}

/**
 * Get the reading progress percentage.
 */
export function getProgressPercentage(progress: ReadingProgress): number {
  return progress.percentage;
}

/**
 * Get the current page from a reading progress.
 * ✅ Renamed from getCurrentPage to avoid conflict with search.ts
 */
export function getReadingCurrentPage(progress: ReadingProgress): number {
  return progress.currentPage;
}

/**
 * Get the total pages from a reading progress.
 * ✅ Renamed from getTotalPages to avoid conflict with search.ts
 */
export function getReadingTotalPages(progress: ReadingProgress): number {
  return progress.totalPages;
}

/**
 * Get the status label for a reading goal.
 */
export function getGoalStatus(goal: ReadingGoal): string {
  if (goal.progressPercentage >= 100) return "Completed 🎉";
  if (goal.progressPercentage >= 75) return "Almost there 🔥";
  if (goal.progressPercentage >= 50) return "Halfway there 📚";
  if (goal.progressPercentage >= 25) return "Getting started 💪";
  return "Just started 🌟";
}

/**
 * Get the status variant for UI display.
 */
export function getGoalStatusVariant(goal: ReadingGoal): "default" | "success" | "warning" | "destructive" {
  if (goal.progressPercentage >= 100) return "success";
  if (goal.progressPercentage >= 50) return "default";
  if (goal.progressPercentage >= 25) return "warning";
  return "destructive";
}

/**
 * Format reading time for display.
 */
export function formatReadingTime(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} min${minutes !== 1 ? "s" : ""}`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  if (remainingMinutes === 0) {
    return `${hours} hour${hours !== 1 ? "s" : ""}`;
  }
  return `${hours}h ${remainingMinutes}min`;
}

/**
 * Get the display text for a reading goal type.
 */
export function getGoalTypeLabel(goalType: ReadingGoalType): string {
  const labels = {
    books: "Books",
    pages: "Pages",
    minutes: "Minutes",
  };
  return labels[goalType] || goalType;
}

/**
 * Get the progress display for a reading goal.
 */
export function getGoalProgressDisplay(goal: ReadingGoal): string {
  const label = getGoalTypeLabel(goal.goalType);
  return `${goal.current} / ${goal.target} ${label.toLowerCase()}`;
}

/**
 * Calculate estimated time left based on reading speed.
 */
export function calculateEstimatedTimeLeft(
  currentPage: number,
  totalPages: number,
  readingSpeed: number = 2 // pages per minute on average
): number | undefined {
  if (currentPage >= totalPages) return 0;
  const pagesLeft = totalPages - currentPage;
  return Math.round(pagesLeft / readingSpeed);
}

/**
 * Get a human-readable time left string.
 */
export function getTimeLeftDisplay(minutes: number | undefined): string | undefined {
  if (minutes === undefined || minutes <= 0) return undefined;
  if (minutes < 60) {
    return `${minutes} min${minutes !== 1 ? "s" : ""}`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  if (remainingMinutes === 0) {
    return `${hours} hour${hours !== 1 ? "s" : ""}`;
  }
  return `${hours}h ${remainingMinutes}min`;
}

/**
 * Check if a reading history item is completed.
 */
export function isHistoryItemCompleted(item: ReadingHistoryItem): boolean {
  return !!item.completedAt || item.progress.percentage >= 100;
}

/**
 * Get the reading duration between start and complete.
 */
export function getReadingDuration(item: ReadingHistoryItem): number | undefined {
  if (!item.completedAt) return undefined;
  const start = new Date(item.startedAt);
  const end = new Date(item.completedAt);
  return Math.round((end.getTime() - start.getTime()) / (1000 * 60)); // minutes
}