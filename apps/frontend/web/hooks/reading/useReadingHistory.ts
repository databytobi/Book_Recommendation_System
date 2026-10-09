/**
 * ================================================================
 * 📜 useReadingHistory Hook
 * ================================================================
 *
 * A custom React hook for fetching and managing reading history.
 * 
 * Features:
 * - Fetches user's reading history on mount
 * - Handles loading and error states
 * - Provides filtering and sorting capabilities
 * - Calculates reading statistics
 * - Caches results to prevent unnecessary requests
 * 
 * @example
 * ```tsx
 * const { history, loading, stats, filterByYear } = useReadingHistory();
 * 
 * if (loading) return <LoadingSpinner />;
 * if (error) return <ErrorMessage error={error} />;
 * 
 * return (
 *   <div>
 *     <p>Total books read: {stats.totalBooks}</p>
 *     <p>Total pages read: {stats.totalPages}</p>
 *     {history.map(item => (
 *       <HistoryItem key={item.id} item={item} />
 *     ))}
 *   </div>
 * );
 * ```
 * ================================================================
 */

import { useEffect, useState, useCallback, useRef, useMemo } from "react";

import { readingService } from "@/lib/services";
import type { ReadingHistoryItem } from "@/lib/types";

// ============================================================
// 📋 Types
// ============================================================

interface UseReadingHistoryOptions {
  /** Automatically fetch on mount (default: true) */
  autoFetch?: boolean;
  
  /** Enable caching (default: true) */
  cache?: boolean;
  
  /** Cache key (default: 'reading-history-cache') */
  cacheKey?: string;
  
  /** Initial filter by year */
  initialYear?: number;
  
  /** Initial sort order */
  initialSort?: "newest" | "oldest" | "rating" | "duration";
}

interface ReadingHistoryStats {
  /** Total books in history */
  totalBooks: number;
  
  /** Total books completed */
  completedBooks: number;
  
  /** Books currently in progress */
  inProgressBooks: number;
  
  /** Total pages read across all books */
  totalPages: number;
  
  /** Average rating */
  averageRating: number;
  
  /** Total reading time in minutes */
  totalReadingTime: number;
  
  /** Average reading time per book */
  averageReadingTime: number;
  
  /** Most active month */
  mostActiveMonth: string;
  
  /** Books read this year */
  booksThisYear: number;
  
  /** Years with reading activity */
  activeYears: number[];
}

interface UseReadingHistoryReturn {
  /** Full reading history */
  history: ReadingHistoryItem[];
  
  /** Filtered history */
  filteredHistory: ReadingHistoryItem[];
  
  /** Whether data is currently loading */
  loading: boolean;
  
  /** Error object if request failed */
  error: Error | null;
  
  /** Reading statistics */
  stats: ReadingHistoryStats;
  
  /** Current filter year */
  filterYear: number | null;
  
  /** Current sort order */
  sortOrder: "newest" | "oldest" | "rating" | "duration";
  
  /** Filter history by year */
  filterByYear: (year: number | null) => void;
  
  /** Change sort order */
  setSortOrder: (order: "newest" | "oldest" | "rating" | "duration") => void;
  
  /** Get history by year */
  getHistoryByYear: (year: number) => ReadingHistoryItem[];
  
  /** Manually refetch history */
  refetch: () => Promise<void>;
  
  /** Clear the cache */
  clearCache: () => void;
  
  /** Reset the hook state */
  reset: () => void;
}

// ============================================================
// 🔧 Hook Implementation
// ============================================================

/**
 * Custom hook for fetching and managing reading history.
 * 
 * @param options - Configuration options
 * @returns {UseReadingHistoryReturn} - History data and utilities
 * 
 * @example
 * ```tsx
 * // Basic usage
 * const { history, loading, stats } = useReadingHistory();
 * 
 * // With options
 * const { history, filteredHistory, filterByYear, setSortOrder } = useReadingHistory({
 *   autoFetch: true,
 *   cache: true,
 *   initialYear: 2024,
 *   initialSort: "newest",
 * });
 * 
 * // Filter by year
 * const handleFilter = (year: number) => {
 *   filterByYear(year);
 * };
 * ```
 */
export function useReadingHistory(options: UseReadingHistoryOptions = {}): UseReadingHistoryReturn {
  const {
    autoFetch = true,
    cache = true,
    cacheKey = 'reading-history-cache',
    initialYear = null,
    initialSort = "newest",
  } = options;

  // ============================================================
  // 📦 State
  // ============================================================

  const [history, setHistory] = useState<ReadingHistoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [filterYear, setFilterYear] = useState<number | null>(initialYear || null);
  const [sortOrder, setSortOrder] = useState<"newest" | "oldest" | "rating" | "duration">(initialSort);
  const isMounted = useRef<boolean>(true);

  // ============================================================
  // 📊 Statistics Calculation
  // ============================================================

  /**
   * Calculate reading statistics from history.
   */
  const calculateStats = useCallback((data: ReadingHistoryItem[]): ReadingHistoryStats => {
    const total = data.length;
    let completed = 0;
    let inProgress = 0;
    let totalPages = 0;
    let totalRating = 0;
    let ratedBooks = 0;
    let totalReadingTime = 0;
    const monthCount: Record<string, number> = {};
    const currentYear = new Date().getFullYear();
    let booksThisYear = 0;
    const activeYears: number[] = [];

    data.forEach((item) => {
      const isCompleted = item.isCompleted || item.progress?.percentage >= 100;
      
      if (isCompleted) {
        completed++;
        if (item.book.rating) {
          totalRating += item.book.rating;
          ratedBooks++;
        }
        if (item.readingDuration) {
          totalReadingTime += item.readingDuration;
        }
      } else {
        inProgress++;
      }

      totalPages += item.progress?.totalPages || 0;

      // Track active months
      const date = new Date(item.startedAt);
      const month = date.toLocaleString('default', { month: 'long' });
      monthCount[month] = (monthCount[month] || 0) + 1;

      // Track active years
      const year = date.getFullYear();
      if (!activeYears.includes(year)) {
        activeYears.push(year);
      }

      // Count books this year
      if (isCompleted && year === currentYear) {
        booksThisYear++;
      }
    });

    // Find most active month
    let mostActiveMonth = '';
    let maxCount = 0;
    for (const [month, count] of Object.entries(monthCount)) {
      if (count > maxCount) {
        maxCount = count;
        mostActiveMonth = month;
      }
    }

    const avgRating = ratedBooks > 0 ? Math.round((totalRating / ratedBooks) * 10) / 10 : 0;
    const avgReadingTime = completed > 0 ? Math.round(totalReadingTime / completed) : 0;

    return {
      totalBooks: total,
      completedBooks: completed,
      inProgressBooks: inProgress,
      totalPages,
      averageRating: avgRating,
      totalReadingTime,
      averageReadingTime: avgReadingTime,
      mostActiveMonth: mostActiveMonth || 'N/A',
      booksThisYear,
      activeYears: activeYears.sort((a, b) => b - a),
    };
  }, []);

  // ============================================================
  // 📊 Filtering and Sorting
  // ============================================================

  /**
   * Filter history by year.
   */
  const filterByYear = useCallback((year: number | null) => {
    setFilterYear(year);
  }, []);

  /**
   * Get filtered and sorted history.
   */
  const getFilteredHistory = useCallback((): ReadingHistoryItem[] => {
    let filtered = [...history];

    // Apply year filter
    if (filterYear) {
      filtered = filtered.filter((item) => {
        const date = new Date(item.startedAt);
        return date.getFullYear() === filterYear;
      });
    }

    // Apply sorting
    switch (sortOrder) {
      case "newest":
        filtered.sort((a, b) => new Date(b.startedAt).getTime() - new Date(a.startedAt).getTime());
        break;
      case "oldest":
        filtered.sort((a, b) => new Date(a.startedAt).getTime() - new Date(b.startedAt).getTime());
        break;
      case "rating":
        filtered.sort((a, b) => (b.book.rating || 0) - (a.book.rating || 0));
        break;
      case "duration":
        filtered.sort((a, b) => (b.readingDuration || 0) - (a.readingDuration || 0));
        break;
      default:
        break;
    }

    return filtered;
  }, [history, filterYear, sortOrder]);

  // ============================================================
  // 📊 Derived State
  // ============================================================

  const stats = useMemo(() => calculateStats(history), [history, calculateStats]);
  const filteredHistory = useMemo(() => getFilteredHistory(), [getFilteredHistory]);

  /**
   * Get history by specific year.
   */
  const getHistoryByYear = useCallback((year: number): ReadingHistoryItem[] => {
    return history.filter((item) => {
      const date = new Date(item.startedAt);
      return date.getFullYear() === year;
    });
  }, [history]);

  // ============================================================
  // 🛠️ Helper Functions
  // ============================================================

  /**
   * Load cached data from localStorage.
   */
  const loadFromCache = useCallback((): ReadingHistoryItem[] | null => {
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
      console.warn('Failed to load reading history from cache:', _err);
    }
    return null;
  }, [cache, cacheKey]);

  /**
   * Save data to cache.
   */
  const saveToCache = useCallback((data: ReadingHistoryItem[]) => {
    if (!cache || typeof window === 'undefined') return;
    
    try {
      localStorage.setItem(cacheKey, JSON.stringify(data));
    } catch (_err) {
      console.warn('Failed to save reading history to cache:', _err);
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
   * Fetch reading history.
   */
  const fetchHistory = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      const data = await readingService.getReadingHistory();
      
      if (isMounted.current) {
        setHistory(data);
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
              setHistory(cached);
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
   * Refetch history.
   */
  // FIX 3: Simplify refetch
  const refetch = useCallback((): Promise<void> => {
    return fetchHistory();
  }, [fetchHistory]);

  /**
   * Reset the hook state.
   */
  // FIX 2: Add void to fetchHistory in reset
  const reset = useCallback(() => {
    setHistory([]);
    setLoading(true);
    setError(null);
    setFilterYear(null);
    setSortOrder("newest");
    clearCache();
    void fetchHistory();
  }, [clearCache, fetchHistory]);

  // ============================================================
  // 🎯 Effects
  // ============================================================

  // FIX 1: Initial fetch on mount with queueMicrotask
  useEffect(() => {
    isMounted.current = true;

    if (cache) {
      const cached = loadFromCache();

      if (cached) {
        queueMicrotask(() => {
          if (!isMounted.current) return;

          setHistory(cached);
          setLoading(false);
        });
      }
    }

    if (autoFetch) {
      let isFetchMounted = true;
      const fetchData = async () => {
        if (isFetchMounted) {
          await fetchHistory();
        }
      };
      fetchData();
      
      return () => {
        isFetchMounted = false;
      };
    }

    return () => {
      isMounted.current = false;
    };
  }, [autoFetch, cache, fetchHistory, loadFromCache]);

  // ============================================================
  // 📦 Return
  // ============================================================

  return {
    history,
    filteredHistory,
    loading,
    error,
    stats,
    filterYear,
    sortOrder,
    filterByYear,
    setSortOrder,
    getHistoryByYear,
    refetch,
    clearCache,
    reset,
  };
}

// ============================================================
// 🔄 Sub-hooks
// ============================================================

/**
 * useReadingHistoryStats - Hook for getting reading statistics only.
 * 
 * @returns ReadingHistoryStats - Reading statistics
 * 
 * @example
 * ```tsx
 * const stats = useReadingHistoryStats();
 * 
 * return (
 *   <div>
 *     <p>📚 {stats.completedBooks} books completed</p>
 *     <p>📖 {stats.totalPages} pages read</p>
 *   </div>
 * );
 * ```
 */
export function useReadingHistoryStats(): ReadingHistoryStats {
  const { stats, loading } = useReadingHistory({ autoFetch: true });
  
  if (loading) {
    return {
      totalBooks: 0,
      completedBooks: 0,
      inProgressBooks: 0,
      totalPages: 0,
      averageRating: 0,
      totalReadingTime: 0,
      averageReadingTime: 0,
      mostActiveMonth: 'N/A',
      booksThisYear: 0,
      activeYears: [],
    };
  }
  
  return stats;
}

/**
 * useYearlyHistory - Hook for getting history by year.
 * 
 * @param year - The year to filter by
 * @returns History items for the specified year
 * 
 * @example
 * ```tsx
 * const history2024 = useYearlyHistory(2024);
 * 
 * return (
 *   <div>
 *     <p>Books read in 2024: {history2024.length}</p>
 *   </div>
 * );
 * ```
 */
export function useYearlyHistory(year: number) {
  const { getHistoryByYear, loading } = useReadingHistory({ autoFetch: true });
  
  const history = getHistoryByYear(year);
  
  return {
    history,
    count: history.length,
    loading,
  };
}

/**
 * useActiveYears - Hook for getting years with reading activity.
 * 
 * @returns Active years
 * 
 * @example
 * ```tsx
 * const { years, loading } = useActiveYears();
 * 
 * return (
 *   <select>
 *     {years.map(year => (
 *       <option key={year} value={year}>{year}</option>
 *     ))}
 *   </select>
 * );
 * ```
 */
export function useActiveYears() {
  const { stats, loading } = useReadingHistory({ autoFetch: true });
  
  return {
    years: stats.activeYears || [],
    loading,
  };
}

// ============================================================
// 📦 Export Default
// ============================================================

export default useReadingHistory;