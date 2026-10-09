/**
 * ================================================================
 * 📖 Reading Service
 * ================================================================
 *
 * Handles all reading-related operations including:
 * - Continue reading books
 * - Recently viewed books
 * - Reading history
 * - Reading goals
 *
 * Currently backed by mock data.
 * Will later communicate with the backend API.
 * ================================================================
 */

import {
  getContinueReadingBooks,
  getRecentlyViewedBooks,
  getReadingHistory,
  getReadingGoals,
  getPrimaryReadingGoal,
  getInProgressBooks,
  getCompletedBooks,
  getTotalPagesRead,
  getAverageProgress,
  getMostRecentView,
  getReadingHistoryByYear,
  getCompletedHistoryItems,
  getReadingStats,
} from "@/lib/mock";

import type {
  ContinueReadingBook,
  ReadingGoal,
  ReadingHistoryItem,
  RecentlyViewedBook,
} from "@/lib/types";

// ============================================================
// 📖 Reading Service Class
// ============================================================

class ReadingService {
  /**
   * Get all books the user is currently reading.
   * 
   * @returns Promise<ContinueReadingBook[]> - Array of books in progress
   * 
   * @example
   * ```ts
   * const reading = await readingService.getContinueReading();
   * console.log(reading); // Books currently being read
   * ```
   */
  async getContinueReading(): Promise<ContinueReadingBook[]> {
    try {
      // In production, this would be an API call:
      // const response = await fetch('/api/reading/continue');
      // return response.json();
      return getContinueReadingBooks();
    } catch (error) {
      console.error("Error fetching continue reading books:", error);
      throw new Error("Failed to fetch continue reading books");
    }
  }

  /**
   * Get books the user has recently viewed.
   * 
   * @returns Promise<RecentlyViewedBook[]> - Array of recently viewed books
   * 
   * @example
   * ```ts
   * const viewed = await readingService.getRecentlyViewed();
   * console.log(viewed); // Recently viewed books
   * ```
   */
  async getRecentlyViewed(): Promise<RecentlyViewedBook[]> {
    try {
      // In production, this would be an API call:
      // const response = await fetch('/api/reading/recently-viewed');
      // return response.json();
      return getRecentlyViewedBooks();
    } catch (error) {
      console.error("Error fetching recently viewed books:", error);
      throw new Error("Failed to fetch recently viewed books");
    }
  }

  /**
   * Get the user's complete reading history.
   * 
   * @returns Promise<ReadingHistoryItem[]> - Array of reading history entries
   * 
   * @example
   * ```ts
   * const history = await readingService.getReadingHistory();
   * console.log(history); // Full reading history
   * ```
   */
  async getReadingHistory(): Promise<ReadingHistoryItem[]> {
    try {
      // In production, this would be an API call:
      // const response = await fetch('/api/reading/history');
      // return response.json();
      return getReadingHistory();
    } catch (error) {
      console.error("Error fetching reading history:", error);
      throw new Error("Failed to fetch reading history");
    }
  }

  /**
   * Get the user's current reading goal.
   * 
   * @returns Promise<ReadingGoal | undefined> - The reading goal if set
   * 
   * @example
   * ```ts
   * const goal = await readingService.getReadingGoal();
   * if (goal) {
   *   console.log(goal.progressPercentage); // Progress percentage
   * }
   * ```
   */
  async getReadingGoal(): Promise<ReadingGoal | undefined> {
    try {
      // In production, this would be an API call:
      // const response = await fetch('/api/reading/goal');
      // return response.json();
      return getPrimaryReadingGoal();
    } catch (error) {
      console.error("Error fetching reading goal:", error);
      throw new Error("Failed to fetch reading goal");
    }
  }

  /**
   * Get all reading goals (if multiple exist).
   * 
   * @returns Promise<ReadingGoal[]> - Array of reading goals
   * 
   * @example
   * ```ts
   * const goals = await readingService.getReadingGoals();
   * console.log(goals); // All reading goals
   * ```
   */
  async getReadingGoals(): Promise<ReadingGoal[]> {
    try {
      // In production, this would be an API call:
      // const response = await fetch('/api/reading/goals');
      // return response.json();
      return getReadingGoals();
    } catch (error) {
      console.error("Error fetching reading goals:", error);
      throw new Error("Failed to fetch reading goals");
    }
  }

  /**
   * Get books that are currently in progress (not completed).
   * 
   * @returns Promise<ContinueReadingBook[]> - Array of in-progress books
   * 
   * @example
   * ```ts
   * const inProgress = await readingService.getInProgressBooks();
   * console.log(inProgress); // Books with 0% < progress < 100%
   * ```
   */
  async getInProgressBooks(): Promise<ContinueReadingBook[]> {
    try {
      return getInProgressBooks();
    } catch (error) {
      console.error("Error fetching in-progress books:", error);
      throw new Error("Failed to fetch in-progress books");
    }
  }

  /**
   * Get books that have been completed.
   * 
   * @returns Promise<ContinueReadingBook[]> - Array of completed books
   * 
   * @example
   * ```ts
   * const completed = await readingService.getCompletedBooks();
   * console.log(completed); // Books with 100% progress
   * ```
   */
  async getCompletedBooks(): Promise<ContinueReadingBook[]> {
    try {
      return getCompletedBooks();
    } catch (error) {
      console.error("Error fetching completed books:", error);
      throw new Error("Failed to fetch completed books");
    }
  }

  /**
   * Get the total number of pages read across all books.
   * 
   * @returns Promise<number> - Total pages read
   * 
   * @example
   * ```ts
   * const pages = await readingService.getTotalPagesRead();
   * console.log(pages); // Total pages read
   * ```
   */
  async getTotalPagesRead(): Promise<number> {
    try {
      return getTotalPagesRead();
    } catch (error) {
      console.error("Error fetching total pages read:", error);
      throw new Error("Failed to fetch total pages read");
    }
  }

  /**
   * Get the average progress percentage across all books.
   * 
   * @returns Promise<number> - Average progress percentage
   * 
   * @example
   * ```ts
   * const avgProgress = await readingService.getAverageProgress();
   * console.log(avgProgress); // Average progress
   * ```
   */
  async getAverageProgress(): Promise<number> {
    try {
      return getAverageProgress();
    } catch (error) {
      console.error("Error fetching average progress:", error);
      throw new Error("Failed to fetch average progress");
    }
  }

  /**
   * Get the most recently viewed book.
   * 
   * @returns Promise<RecentlyViewedBook | undefined> - Most recent view
   * 
   * @example
   * ```ts
   * const recent = await readingService.getMostRecentView();
   * console.log(recent); // Most recently viewed book
   * ```
   */
  async getMostRecentView(): Promise<RecentlyViewedBook | undefined> {
    try {
      return getMostRecentView();
    } catch (error) {
      console.error("Error fetching most recent view:", error);
      throw new Error("Failed to fetch most recent view");
    }
  }

  /**
   * Get reading history filtered by year.
   * 
   * @param year - The year to filter by
   * @returns Promise<ReadingHistoryItem[]> - Filtered reading history
   * 
   * @example
   * ```ts
   * const history2024 = await readingService.getReadingHistoryByYear(2024);
   * console.log(history2024); // Reading history from 2024
   * ```
   */
  async getReadingHistoryByYear(year: number): Promise<ReadingHistoryItem[]> {
    if (!year || year < 2000) {
      throw new Error("Invalid year provided");
    }

    try {
      return getReadingHistoryByYear(year);
    } catch (error) {
      console.error(`Error fetching reading history for year ${year}:`, error);
      throw new Error(`Failed to fetch reading history for year ${year}`);
    }
  }

  /**
   * Get completed reading history items.
   * 
   * @returns Promise<ReadingHistoryItem[]> - Completed history items
   * 
   * @example
   * ```ts
   * const completed = await readingService.getCompletedHistoryItems();
   * console.log(completed); // Completed reading history
   * ```
   */
  async getCompletedHistoryItems(): Promise<ReadingHistoryItem[]> {
    try {
      return getCompletedHistoryItems();
    } catch (error) {
      console.error("Error fetching completed history items:", error);
      throw new Error("Failed to fetch completed history items");
    }
  }

  /**
   * Get reading statistics summary.
   * 
   * @returns Promise<Object> - Reading statistics
   * 
   * @example
   * ```ts
   * const stats = await readingService.getReadingStats();
   * console.log(stats.totalBooks); // Total books
   * ```
   */
  async getReadingStats() {
    try {
      return getReadingStats();
    } catch (error) {
      console.error("Error fetching reading stats:", error);
      throw new Error("Failed to fetch reading stats");
    }
  }

  /**
   * Update reading progress for a book.
   * 
   * @param bookId - The book ID
   * @param currentPage - The current page number
   * @returns Promise<ContinueReadingBook> - Updated book
   * 
   * @example
   * ```ts
   * const updated = await readingService.updateProgress(1, 150);
   * console.log(updated.progress.percentage); // Updated progress
   * ```
   */
  async updateProgress(bookId: number, currentPage: number): Promise<ContinueReadingBook> {
    if (!bookId || bookId <= 0) {
      throw new Error("Invalid book ID");
    }

    if (currentPage < 0) {
      throw new Error("Invalid page number");
    }

    try {
      // In production, this would be an API call:
      // const response = await fetch(`/api/reading/progress`, {
      //   method: 'PUT',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ bookId, currentPage }),
      // });
      // return response.json();

      // Mock implementation - find and update the book
      const books = await this.getContinueReading();
      const book = books.find((b) => b.id === bookId);
      
      if (!book) {
        throw new Error(`Book with ID ${bookId} not found in reading list`);
      }

      // Update progress
      const updatedBook = {
        ...book,
        progress: {
          ...book.progress,
          currentPage,
          percentage: Math.min(Math.round((currentPage / book.progress.totalPages) * 100), 100),
          lastReadAt: new Date().toISOString(),
        },
      };

      return updatedBook;
    } catch (error) {
      console.error(`Error updating progress for book ${bookId}:`, error);
      throw new Error(`Failed to update progress for book ${bookId}`);
    }
  }

  /**
   * Check if a book is in the user's reading list.
   * 
   * @param bookId - The book ID to check
   * @returns Promise<boolean> - True if the book is in the reading list
   * 
   * @example
   * ```ts
   * const isReading = await readingService.isReadingBook(1);
   * console.log(isReading); // true or false
   * ```
   */
  async isReadingBook(bookId: number): Promise<boolean> {
    if (!bookId || bookId <= 0) {
      return false;
    }

    try {
      const books = await this.getContinueReading();
      return books.some((book) => book.id === bookId);
    } catch (error) {
      console.error(`Error checking if book ${bookId} is being read:`, error);
      return false;
    }
  }
}

// ============================================================
// 📦 Export Singleton Instance
// ============================================================

export const readingService = new ReadingService();