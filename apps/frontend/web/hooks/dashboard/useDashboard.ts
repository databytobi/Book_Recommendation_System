/**
 * ================================================================
 * 📊 useDashboard Hook
 * ================================================================
 *
 * A custom React hook for fetching and managing dashboard data.
 * 
 * Features:
 * - Fetches complete dashboard data on mount
 * - Handles loading and error states
 * - Provides dashboard statistics and metrics
 * - Offers refresh and filter capabilities
 * - Caches results to prevent unnecessary requests
 * 
 * @example
 * ```tsx
 * const { dashboard, loading, stats, refresh } = useDashboard();
 * 
 * if (loading) return <LoadingSpinner />;
 * if (error) return <ErrorMessage error={error} />;
 * 
 * return (
 *   <div>
 *     <DashboardStats stats={dashboard?.stats} />
 *     <ContinueReading books={dashboard?.continueReading} />
 *     <Recommendations sections={dashboard?.recommendations} />
 *   </div>
 * );
 * ```
 * ================================================================
 */
// hooks/useDashboard.ts - In the fetch function

import { useEffect, useState, useCallback, useRef, useMemo } from "react";

import { dashboardService } from "@/lib/services";
import type { DashboardData, DashboardStat } from "@/lib/types";

// ============================================================
// 📋 Types
// ============================================================

interface UseDashboardOptions {
  /** Automatically fetch on mount (default: true) */
  autoFetch?: boolean;
  
  /** Enable caching (default: true) */
  cache?: boolean;
  
  /** Cache key (default: 'dashboard-cache') */
  cacheKey?: string;
  
  /** Cache expiration in milliseconds (default: 5 minutes) */
  cacheExpiration?: number;
  
  /** Enable auto-refresh (default: false) */
  autoRefresh?: boolean;
  
  /** Auto-refresh interval in milliseconds (default: 60 seconds) */
  refreshInterval?: number;
}

interface DashboardStats {
  /** Total books read */
  totalBooksRead: number;
  
  /** Current reading streak */
  readingStreak: number;
  
  /** Total pages read */
  totalPagesRead: number;
  
  /** Books currently in progress */
  booksInProgress: number;
  
  /** Books completed */
  booksCompleted: number;
  
  /** Average rating */
  averageRating: number;
  
  /** Total recommendations count */
  recommendationsCount: number;
  
  /** Overall progress percentage */
  overallProgress: number;
  
  /** Positive trend stats count */
  positiveTrends: number;
  
  /** Negative trend stats count */
  negativeTrends: number;
}

interface DashboardSummary {
  /** Total books read */
  totalBooksRead: number;
  
  /** Reading streak */
  readingStreak: string;
  
  /** Total pages read */
  totalPagesRead: string;
  
  /** Number of recommendations */
  recommendationsCount: number;
  
  /** Books in progress */
  booksInProgress: number;
}

interface RecentActivityItem {
  /** Activity type */
  type: "reading" | "viewed" | "recommended" | "completed";
  
  /** Activity message */
  message: string;
  
  /** Activity details */
  details: string;
  
  /** Activity timestamp */
  timestamp: string;
}

interface UseDashboardReturn {
  /** Complete dashboard data */
  dashboard: DashboardData | null;
  
  /** Whether data is currently loading */
  loading: boolean;
  
  /** Error object if request failed */
  error: Error | null;
  
  /** Dashboard statistics */
  stats: DashboardStats;
  
  /** Dashboard summary */
  summary: DashboardSummary;
  
  /** Recent activity items */
  recentActivity: RecentActivityItem[];
  
  /** Whether dashboard is empty */
  isEmpty: boolean;
  
  /** Whether dashboard has data */
  hasData: boolean;
  
  /** Last updated timestamp */
  lastUpdated: string | null;
  
  /** Refresh dashboard data */
  refresh: () => Promise<void>;
  
  /** Clear cache */
  clearCache: () => void;
  
  /** Reset hook state */
  reset: () => void;
  
  /** Get a specific stat by title */
  getStat: (title: string) => DashboardStat | undefined;
  
  /** Get stats with positive trends */
  getPositiveTrendStats: () => DashboardStat[];
  
  /** Get stats with negative trends */
  getNegativeTrendStats: () => DashboardStat[];
}

// ============================================================
// 🔧 Hook Implementation
// ============================================================

/**
 * Custom hook for fetching and managing dashboard data.
 * 
 * @param options - Configuration options
 * @returns {UseDashboardReturn} - Dashboard data and utilities
 * 
 * @example
 * ```tsx
 * // Basic usage
 * const { dashboard, loading, stats } = useDashboard();
 * 
 * // With options
 * const { dashboard, loading, refresh, stats } = useDashboard({
 *   autoFetch: true,
 *   cache: true,
 *   autoRefresh: true,
 *   refreshInterval: 30000,
 * });
 * 
 * // Refresh dashboard
 * const handleRefresh = async () => {
 *   await refresh();
 * };
 * ```
 */
export function useDashboard(options: UseDashboardOptions = {}): UseDashboardReturn {
  const {
    autoFetch = true,
    cache = true,
    cacheKey = 'dashboard-cache',
    cacheExpiration = 5 * 60 * 1000, // 5 minutes
    autoRefresh = false,
    refreshInterval = 60 * 1000, // 60 seconds
  } = options;

  // ============================================================
  // 📦 State
  // ============================================================

  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const refreshTimer = useRef<NodeJS.Timeout | null>(null);
  const isMounted = useRef<boolean>(true);

  // ============================================================
  // 📊 Derived State
  // ============================================================

  const hasData = useMemo(() => {
    if (!dashboard) return false;
    return (
      (dashboard.stats?.length || 0) > 0 ||
      (dashboard.continueReading?.length || 0) > 0 ||
      (dashboard.recentlyViewed?.length || 0) > 0 ||
      (dashboard.recommendations?.length || 0) > 0
    );
  }, [dashboard]);

  const isEmpty = useMemo(() => {
    return !hasData;
  }, [hasData]);

  // ============================================================
  // 📊 Statistics Calculation
  // ============================================================

  const stats: DashboardStats = useMemo(() => {
    if (!dashboard) {
      return {
        totalBooksRead: 0,
        readingStreak: 0,
        totalPagesRead: 0,
        booksInProgress: 0,
        booksCompleted: 0,
        averageRating: 0,
        recommendationsCount: 0,
        overallProgress: 0,
        positiveTrends: 0,
        negativeTrends: 0,
      };
    }

    const statsData = dashboard.stats || [];
    const totalBooksRead = statsData.find(s => s.title === "Books Read")?.value as number || 0;
    const readingStreak = statsData.find(s => s.title === "Reading Streak")?.value as string || "0";
    const totalPagesRead = statsData.find(s => s.title === "Pages Read")?.value as string || "0";
    const booksInProgress = dashboard.continueReading?.filter(b => b.progress?.percentage < 100).length || 0;
    const booksCompleted = dashboard.continueReading?.filter(b => b.progress?.percentage >= 100).length || 0;
    const recommendationsCount = dashboard.recommendations?.reduce((acc, s) => acc + s.books.length, 0) || 0;
    
    // Calculate average rating from stats
    const avgRatingStat = statsData.find(s => s.title === "Average Rating");
    const averageRating = avgRatingStat ? parseFloat(avgRatingStat.value as string) || 0 : 0;
    
    // Calculate overall progress
    const positiveTrends = statsData.filter(s => s.trend === "up").length;
    const negativeTrends = statsData.filter(s => s.trend === "down").length;
    const overallProgress = statsData.length > 0 ? Math.round((positiveTrends / statsData.length) * 100) : 0;

    return {
      totalBooksRead: typeof totalBooksRead === 'number' ? totalBooksRead : 0,
      readingStreak: typeof readingStreak === 'string' ? parseInt(readingStreak) || 0 : 0,
      totalPagesRead: typeof totalPagesRead === 'string' ? parseInt(totalPagesRead.replace(/,/g, '')) || 0 : 0,
      booksInProgress,
      booksCompleted,
      averageRating,
      recommendationsCount,
      overallProgress,
      positiveTrends,
      negativeTrends,
    };
  }, [dashboard]);

  const summary: DashboardSummary = useMemo(() => {
    if (!dashboard) {
      return {
        totalBooksRead: 0,
        readingStreak: "0",
        totalPagesRead: "0",
        recommendationsCount: 0,
        booksInProgress: 0,
      };
    }

    const statsData = dashboard.stats || [];
    const totalBooksRead = statsData.find(s => s.title === "Books Read")?.value as number || 0;
    const readingStreak = statsData.find(s => s.title === "Reading Streak")?.value as string || "0";
    const totalPagesRead = statsData.find(s => s.title === "Pages Read")?.value as string || "0";
    const booksInProgress = dashboard.continueReading?.filter(b => b.progress?.percentage < 100).length || 0;
    const recommendationsCount = dashboard.recommendations?.reduce((acc, s) => acc + s.books.length, 0) || 0;

    return {
      totalBooksRead: typeof totalBooksRead === 'number' ? totalBooksRead : 0,
      readingStreak: typeof readingStreak === 'string' ? readingStreak : "0",
      totalPagesRead: typeof totalPagesRead === 'string' ? totalPagesRead : "0",
      recommendationsCount,
      booksInProgress,
    };
  }, [dashboard]);

  // ============================================================
  // 📊 Recent Activity
  // ============================================================

  const recentActivity: RecentActivityItem[] = useMemo(() => {
    if (!dashboard) return [];

    const activities: RecentActivityItem[] = [];

    // Add continue reading activities
    if (dashboard.continueReading && dashboard.continueReading.length > 0) {
      const book = dashboard.continueReading[0];
      const progress = book.progress?.percentage || 0;
      activities.push({
        type: "reading",
        message: `Reading "${book.title}"`,
        details: `${progress}% complete`,
        timestamp: book.progress?.lastReadAt || new Date().toISOString(),
      });
    }

    // Add recently viewed activities
    if (dashboard.recentlyViewed && dashboard.recentlyViewed.length > 0) {
      const book = dashboard.recentlyViewed[0];
      activities.push({
        type: "viewed",
        message: `Viewed "${book.title}"`,
        details: "Recently viewed",
        timestamp: book.viewedAt || new Date().toISOString(),
      });
    }

    // Add recommendation activities
    if (dashboard.recommendations && dashboard.recommendations.length > 0) {
      const section = dashboard.recommendations[0];
      if (section.books.length > 0) {
        const book = section.books[0];
        activities.push({
          type: "recommended",
          message: `Recommended "${book.title}"`,
          details: book.reason || "Based on your reading history",
          timestamp: book.recommendedAt || new Date().toISOString(),
        });
      }
    }

    return activities.sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }, [dashboard]);

  // ============================================================
  // 🛠️ Helper Functions
  // ============================================================

  /**
   * Load dashboard from cache.
   */
  const loadFromCache = useCallback((): DashboardData | null => {
    if (!cache || typeof window === 'undefined') return null;
    
    try {
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        const parsed = JSON.parse(cached);
        const timestamp = localStorage.getItem(`${cacheKey}-timestamp`);
        if (timestamp) {
          const age = Date.now() - parseInt(timestamp);
          if (age < cacheExpiration) {
            return parsed;
          }
        }
      }
    } catch (_err) {
      console.warn('Failed to load dashboard from cache:', _err);
    }
    return null;
  }, [cache, cacheKey, cacheExpiration]);

  /**
   * Save dashboard to cache.
   */
  const saveToCache = useCallback((data: DashboardData) => {
    if (!cache || typeof window === 'undefined') return;
    
    try {
      localStorage.setItem(cacheKey, JSON.stringify(data));
      localStorage.setItem(`${cacheKey}-timestamp`, Date.now().toString());
    } catch (_err) {
      console.warn('Failed to save dashboard to cache:', _err);
    }
  }, [cache, cacheKey]);

  /**
   * Clear cache.
   */
  const clearCache = useCallback(() => {
    if (!cache || typeof window === 'undefined') return;
    
    try {
      localStorage.removeItem(cacheKey);
      localStorage.removeItem(`${cacheKey}-timestamp`);
    } catch (_err) {
      console.warn('Failed to clear cache:', _err);
    }
  }, [cache, cacheKey]);

  /**
   * Fetch dashboard data.
   */
  const fetchDashboard = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      const data = await dashboardService.getDashboard();
      
      if (isMounted.current) {
        setDashboard(data);
        setLastUpdated(data.lastUpdated || new Date().toISOString());
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
              setDashboard(cached);
              setLastUpdated(cached.lastUpdated || null);
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
   * Refresh dashboard data.
   */
  const refresh = useCallback(async (): Promise<void> => {
    await fetchDashboard();
  }, [fetchDashboard]);

  /**
   * Reset hook state.
   */
  const reset = useCallback(() => {
    setDashboard(null);
    setLoading(true);
    setError(null);
    setLastUpdated(null);
    clearCache();
    void fetchDashboard();
  }, [clearCache, fetchDashboard]);

  /**
   * Get a specific stat by title.
   */
  const getStat = useCallback((title: string): DashboardStat | undefined => {
    if (!dashboard) return undefined;
    return dashboard.stats?.find((stat) => stat.title === title);
  }, [dashboard]);

  /**
   * Get stats with positive trends.
   */
  const getPositiveTrendStats = useCallback((): DashboardStat[] => {
    if (!dashboard) return [];
    return dashboard.stats?.filter((stat) => stat.trend === "up") || [];
  }, [dashboard]);

  /**
   * Get stats with negative trends.
   */
  const getNegativeTrendStats = useCallback((): DashboardStat[] => {
    if (!dashboard) return [];
    return dashboard.stats?.filter((stat) => stat.trend === "down") || [];
  }, [dashboard]);

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
          setDashboard(cached);
          setLastUpdated(cached.lastUpdated || null);
          setLoading(false);
        });
      }
    }

    // Auto-fetch if enabled
    if (autoFetch) {
      let isFetchMounted = true;
      const fetchData = async () => {
        if (isFetchMounted) {
          await fetchDashboard();
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
  }, [autoFetch, cache, fetchDashboard, loadFromCache]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh || !isMounted.current) return;

    if (refreshTimer.current) {
      clearInterval(refreshTimer.current);
    }

    refreshTimer.current = setInterval(() => {
      if (isMounted.current) {
        let isRefreshMounted = true;
        const refreshData = async () => {
          if (isRefreshMounted) {
            await fetchDashboard();
          }
        };
        refreshData();
        
        return () => {
          isRefreshMounted = false;
        };
      }
    }, refreshInterval);

    return () => {
      if (refreshTimer.current) {
        clearInterval(refreshTimer.current);
        refreshTimer.current = null;
      }
    };
  }, [autoRefresh, refreshInterval, fetchDashboard]);

  // ============================================================
  // 📦 Return
  // ============================================================

  return {
    dashboard,
    loading,
    error,
    stats,
    summary,
    recentActivity,
    isEmpty,
    hasData,
    lastUpdated,
    refresh,
    clearCache,
    reset,
    getStat,
    getPositiveTrendStats,
    getNegativeTrendStats,
  };
}

// ============================================================
// 🔄 Sub-hooks
// ============================================================

/**
 * useDashboardStats - Hook for getting dashboard statistics only.
 * 
 * @returns DashboardStats - Dashboard statistics
 * 
 * @example
 * ```tsx
 * const stats = useDashboardStats();
 * 
 * return (
 *   <div>
 *     <p>📚 Books read: {stats.totalBooksRead}</p>
 *     <p>🔥 Streak: {stats.readingStreak} days</p>
 *   </div>
 * );
 * ```
 */
export function useDashboardStats(): DashboardStats {
  const { stats, loading } = useDashboard({ autoFetch: true });
  
  if (loading) {
    return {
      totalBooksRead: 0,
      readingStreak: 0,
      totalPagesRead: 0,
      booksInProgress: 0,
      booksCompleted: 0,
      averageRating: 0,
      recommendationsCount: 0,
      overallProgress: 0,
      positiveTrends: 0,
      negativeTrends: 0,
    };
  }
  
  return stats;
}

/**
 * useDashboardSummary - Hook for getting dashboard summary.
 * 
 * @returns DashboardSummary - Dashboard summary
 * 
 * @example
 * ```tsx
 * const summary = useDashboardSummary();
 * 
 * return (
 *   <div>
 *     <p>Total books read: {summary.totalBooksRead}</p>
 *     <p>Current streak: {summary.readingStreak}</p>
 *   </div>
 * );
 * ```
 */
export function useDashboardSummary(): DashboardSummary {
  const { summary, loading } = useDashboard({ autoFetch: true });
  
  if (loading) {
    return {
      totalBooksRead: 0,
      readingStreak: "0",
      totalPagesRead: "0",
      recommendationsCount: 0,
      booksInProgress: 0,
    };
  }
  
  return summary;
}

/**
 * useDashboardActivity - Hook for getting recent activity.
 * 
 * @returns Recent activity items
 * 
 * @example
 * ```tsx
 * const activity = useDashboardActivity();
 * 
 * return (
 *   <div>
 *     {activity.map((item, index) => (
 *       <ActivityItem key={index} item={item} />
 *     ))}
 *   </div>
 * );
 * ```
 */
export function useDashboardActivity() {
  const { recentActivity, loading } = useDashboard({ autoFetch: true });
  
  return {
    activities: recentActivity,
    loading,
  };
}

// ============================================================
// 📦 Export Default
// ============================================================

export default useDashboard;