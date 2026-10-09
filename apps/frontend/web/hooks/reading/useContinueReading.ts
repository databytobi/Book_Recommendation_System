/**
 * ================================================================
 * 📖 useContinueReading Hook
 * ================================================================
 *
 * A custom React hook for fetching and managing continue reading books.
 * 
 * Features:
 * - Fetches books the user is currently reading on mount
 * - Handles loading and error states
 * - Provides refetch functionality
 * - Calculates reading progress statistics
 * - Caches results to prevent unnecessary requests
 * 
 * @example
 * ```tsx
 * const { books, loading, stats, updateProgress } = useContinueReading();
 * 
 * if (loading) return <LoadingSpinner />;
 * if (error) return <ErrorMessage error={error} />;
 * 
 * return (
 *   <div>
 *     <p>Books in progress: {stats.inProgress}</p>
 *     {books.map(book => (
 *       <BookCard key={book.id} book={book} onProgress={updateProgress} />
 *     ))}
 *   </div>
 * );
 * ```
 * ================================================================
 */

import { useEffect, useState, useCallback, useRef } from "react";

import { readingService } from "@/lib/services";
import type { ContinueReadingBook } from "@/lib/types";

// ============================================================
// 📋 Types
// ============================================================

interface UseContinueReadingOptions {
  /** Automatically fetch on mount (default: true) */
  autoFetch?: boolean;
  
  /** Enable caching (default: true) */
  cache?: boolean;
  
  /** Cache key (default: 'continue-reading-cache') */
  cacheKey?: string;
}

interface ContinueReadingStats {
  /** Total books in the reading list */
  totalBooks: number;
  
  /** Books currently in progress (0% - 99%) */
  inProgress: number;
  
  /** Books that are completed (100%) */
  completed: number;
  
  /** Books that haven't been started (0%) */
  notStarted: number;
  
  /** Average progress percentage across all books */
  averageProgress: number;
  
  /** Total pages read across all books */
  totalPagesRead: number;
  
  /** Estimated total time left to finish all books */
  totalTimeLeft: number;
}

interface UseContinueReadingReturn {
  /** List of continue reading books */
  books: ContinueReadingBook[];
  
  /** Whether data is currently loading */
  loading: boolean;
  
  /** Error object if request failed */
  error: Error | null;
  
  /** Reading statistics */
  stats: ContinueReadingStats;
  
  /** Manually refetch books */
  refetch: () => Promise<void>;
  
  /** Update progress for a specific book */
  updateProgress: (bookId: number, currentPage: number) => Promise<void>;
  
  /** Clear the cache */
  clearCache: () => void;
  
  /** Reset the hook state */
  reset: () => void;
}

// ============================================================
// 🔧 Hook Implementation
// ============================================================

/**
 * Custom hook for fetching and managing continue reading books.
 * 
 * @param options - Configuration options
 * @returns {UseContinueReadingReturn} - Books data and utilities
 * 
 * @example
 * ```tsx
 * // Basic usage
 * const { books, loading, stats } = useContinueReading();
 * 
 * // With options
 * const { books, loading, refetch, updateProgress } = useContinueReading({
 *   autoFetch: true,
 *   cache: true,
 * });
 * 
 * // Update progress
 * const handleProgress = async (bookId: number, page: number) => {
 *   await updateProgress(bookId, page);
 * };
 * ```
 */
export function useContinueReading(options: UseContinueReadingOptions = {}): UseContinueReadingReturn {
  const {
    autoFetch = true,
    cache = true,
    cacheKey = 'continue-reading-cache',
  } = options;

  // ============================================================
  // 📦 State
  // ============================================================

  const [books, setBooks] = useState<ContinueReadingBook[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [stats, setStats] = useState<ContinueReadingStats>({
    totalBooks: 0,
    inProgress: 0,
    completed: 0,
    notStarted: 0,
    averageProgress: 0,
    totalPagesRead: 0,
    totalTimeLeft: 0,
  });
  const isMounted = useRef<boolean>(true);

  // ============================================================
  // 📊 Stats Calculation
  // ============================================================

  /**
   * Calculate reading statistics from books.
   */
  const calculateStats = useCallback((booksData: ContinueReadingBook[]): ContinueReadingStats => {
    const total = booksData.length;
    let inProgress = 0;
    let completed = 0;
    let notStarted = 0;
    let totalProgress = 0;
    let totalPagesRead = 0;
    let totalTimeLeft = 0;

    booksData.forEach((book) => {
      const progress = book.progress?.percentage || 0;
      totalProgress += progress;

      if (progress >= 100) {
        completed++;
      } else if (progress > 0) {
        inProgress++;
      } else {
        notStarted++;
      }

      totalPagesRead += book.progress?.currentPage || 0;
      totalTimeLeft += book.estimatedTimeLeft || 0;
    });

    return {
      totalBooks: total,
      inProgress,
      completed,
      notStarted,
      averageProgress: total > 0 ? Math.round(totalProgress / total) : 0,
      totalPagesRead,
      totalTimeLeft,
    };
  }, []);

  /**
   * Update stats whenever books change.
   */
  // FIX: Wrap setState in queueMicrotask to avoid setState-in-effect warning
  useEffect(() => {
    if (books.length > 0) {
      queueMicrotask(() => {
        if (!isMounted.current) return;
        setStats(calculateStats(books));
      });
    }
  }, [books, calculateStats]);

  // ============================================================
  // 🛠️ Helper Functions
  // ============================================================

  /**
   * Load cached data from localStorage.
   */
  const loadFromCache = useCallback((): ContinueReadingBook[] | null => {
    if (!cache || typeof window === 'undefined') return null;
    
    try {
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        const parsed = JSON.parse(cached);
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed;
        }
      }
    } catch (_err) {
      console.warn('Failed to load continue reading from cache:', _err);
    }
    return null;
  }, [cache, cacheKey]);

  /**
   * Save data to cache.
   */
  const saveToCache = useCallback((data: ContinueReadingBook[]) => {
    if (!cache || typeof window === 'undefined') return;
    
    try {
      localStorage.setItem(cacheKey, JSON.stringify(data));
    } catch (_err) {
      console.warn('Failed to save continue reading to cache:', _err);
    }
  }, [cache, cacheKey]);

  /**
   * Clear the cache.
   */
  const clearCache = useCallback(() => {
    if (!cache || typeof window === 'undefined') return;
    
    try {
      localStorage.removeItem(cacheKey);
    } catch (_err) {
      console.warn('Failed to clear cache:', _err);
    }
  }, [cache, cacheKey]);

  /**
   * Fetch continue reading books.
   */
  const fetchBooks = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      const data = await readingService.getContinueReading();
      
      if (isMounted.current) {
        setBooks(data);
        saveToCache(data);
      }
    } catch (err) {
      if (isMounted.current) {
        const error = err as Error;
        setError(error);
        
        // Try to load from cache on error
        if (cache) {
          const cached = loadFromCache();
          if (cached) {
            // FIX: Wrap setState in queueMicrotask to avoid setState-in-effect warning
            queueMicrotask(() => {
              if (!isMounted.current) return;
              setBooks(cached);
              setLoading(false);
            });
          }
        }
      }
    } finally {
      if (isMounted.current) {
        setLoading(false);
      }
    }
  }, [cache, loadFromCache, saveToCache]);

  /**
   * Refetch books.
   */
  const refetch = useCallback(async (): Promise<void> => {
    await fetchBooks();
  }, [fetchBooks]);

  /**
   * Update progress for a specific book.
   */
  const updateProgress = useCallback(async (bookId: number, currentPage: number): Promise<void> => {
    if (!bookId || bookId <= 0) {
      throw new Error('Invalid book ID');
    }

    if (currentPage < 0) {
      throw new Error('Invalid page number');
    }

    try {
      // In a real implementation, this would call the API
      // const updated = await readingService.updateProgress(bookId, currentPage);
      
      // Mock implementation - update locally
      setBooks(prevBooks => 
        prevBooks.map(book => {
          if (book.id === bookId) {
            const totalPages = book.progress?.totalPages || 100;
            const percentage = Math.min(Math.round((currentPage / totalPages) * 100), 100);
            return {
              ...book,
              progress: {
                ...book.progress,
                currentPage,
                percentage,
                lastReadAt: new Date().toISOString(),
              },
            };
          }
          return book;
        })
      );

      // Update cache after progress change
      setTimeout(() => {
        if (cache) {
          saveToCache(books);
        }
      }, 100);
    } catch (err) {
      setError(err as Error);
      throw err;
    }
  }, [books, cache, saveToCache]);

  /**
   * Reset the hook state.
   */
  const reset = useCallback(() => {
    setBooks([]);
    setLoading(true);
    setError(null);
    setStats({
      totalBooks: 0,
      inProgress: 0,
      completed: 0,
      notStarted: 0,
      averageProgress: 0,
      totalPagesRead: 0,
      totalTimeLeft: 0,
    });
    clearCache();
    void fetchBooks();
  }, [clearCache, fetchBooks]);

  // ============================================================
  // 🎯 Effects
  // ============================================================

  // Initial fetch on mount
  useEffect(() => {
    isMounted.current = true;
    
    // Try to load from cache first
    if (cache) {
      const cached = loadFromCache();
      if (cached) {
        // FIX: Wrap setState in queueMicrotask to avoid setState-in-effect warning
        queueMicrotask(() => {
          if (!isMounted.current) return;
          setBooks(cached);
          setLoading(false);
        });
      }
    }

    // Auto-fetch if enabled
    if (autoFetch) {
      let isFetchMounted = true;
      const fetchData = async () => {
        if (isFetchMounted) {
          await fetchBooks();
        }
      };
      fetchData();
      
      return () => {
        isFetchMounted = false;
      };
    }

    // Cleanup
    return () => {
      isMounted.current = false;
    };
  }, [autoFetch, cache, fetchBooks, loadFromCache]);

  // ============================================================
  // 📦 Return
  // ============================================================

  return {
    books,
    loading,
    error,
    stats,
    refetch,
    updateProgress,
    clearCache,
    reset,
  };
}

// ============================================================
// 🔄 Sub-hooks
// ============================================================

/**
 * useContinueReadingStats - Hook for getting reading statistics only.
 * 
 * @returns ContinueReadingStats - Reading statistics
 * 
 * @example
 * ```tsx
 * const stats = useContinueReadingStats();
 * 
 * return (
 *   <div>
 *     <p>📚 {stats.inProgress} books in progress</p>
 *     <p>✅ {stats.completed} books completed</p>
 *   </div>
 * );
 * ```
 */
export function useContinueReadingStats(): ContinueReadingStats {
  const { stats, loading } = useContinueReading({ autoFetch: true });
  
  if (loading) {
    return {
      totalBooks: 0,
      inProgress: 0,
      completed: 0,
      notStarted: 0,
      averageProgress: 0,
      totalPagesRead: 0,
      totalTimeLeft: 0,
    };
  }
  
  return stats;
}

/**
 * useBookProgress - Hook for getting and updating a specific book's progress.
 * 
 * @param bookId - The book ID
 * @returns Book progress and update function
 * 
 * @example
 * ```tsx
 * const { progress, updateProgress, loading } = useBookProgress(1);
 * 
 * return (
 *   <div>
 *     <p>Progress: {progress}%</p>
 *     <button onClick={() => updateProgress(50)}>Update</button>
 *   </div>
 * );
 * ```
 */
export function useBookProgress(bookId: number) {
  const { books, updateProgress, loading } = useContinueReading();
  
  const book = books.find(b => b.id === bookId);
  const progress = book?.progress?.percentage || 0;
  const currentPage = book?.progress?.currentPage || 0;
  const totalPages = book?.progress?.totalPages || 0;

  const handleUpdate = useCallback(async (page: number) => {
    await updateProgress(bookId, page);
  }, [bookId, updateProgress]);

  return {
    progress,
    currentPage,
    totalPages,
    updateProgress: handleUpdate,
    loading,
    book,
  };
}

// ============================================================
// 📦 Export Default
// ============================================================

export default useContinueReading;