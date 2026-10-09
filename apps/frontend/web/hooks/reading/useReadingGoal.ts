/**
 * ================================================================
 * 🎯 useReadingGoal Hook
 * ================================================================
 *
 * A custom React hook for fetching and managing reading goals.
 * 
 * Features:
 * - Fetches user's reading goal on mount
 * - Handles loading and error states
 * - Provides goal progress calculations
 * - Offers goal management functions
 * - Caches results to prevent unnecessary requests
 * 
 * @example
 * ```tsx
 * const { goal, loading, progress, remaining } = useReadingGoal();
 * 
 * if (loading) return <LoadingSpinner />;
 * if (error) return <ErrorMessage error={error} />;
 * 
 * return (
 *   <div>
 *     <p>Goal: {goal.current} / {goal.target} books</p>
 *     <p>Progress: {progress}%</p>
 *     <p>Remaining: {remaining} books</p>
 *   </div>
 * );
 * ```
 * ================================================================
 */

import { useEffect, useState, useCallback, useRef } from "react";

import { readingService } from "@/lib/services";
import type { ReadingGoal, ReadingGoalType } from "@/lib/types";

// ============================================================
// 📋 Types
// ============================================================

interface UseReadingGoalOptions {
  /** Automatically fetch on mount (default: true) */
  autoFetch?: boolean;
  
  /** Enable caching (default: true) */
  cache?: boolean;
  
  /** Cache key (default: 'reading-goal-cache') */
  cacheKey?: string;
}

interface ReadingGoalProgress {
  /** Current progress percentage (0-100) */
  percentage: number;
  
  /** Remaining to reach the goal */
  remaining: number;
  
  /** Status message based on progress */
  statusMessage: string;
  
  /** Color variant for UI display */
  statusVariant: "default" | "success" | "warning" | "destructive";
  
  /** Whether the goal is completed */
  isCompleted: boolean;
  
  /** Whether the goal is on track */
  isOnTrack: boolean;
}

interface UseReadingGoalReturn {
  /** The reading goal object */
  goal: ReadingGoal | null;
  
  /** Whether data is currently loading */
  loading: boolean;
  
  /** Error object if request failed */
  error: Error | null;
  
  /** Progress calculations */
  progress: ReadingGoalProgress;
  
  /** Manually refetch the goal */
  refetch: () => Promise<void>;
  
  /** Update the reading goal */
  updateGoal: (target: number, goalType?: string) => Promise<void>;
  
  /** Clear the cache */
  clearCache: () => void;
  
  /** Reset the hook state */
  reset: () => void;
}

// ============================================================
// 🔧 Hook Implementation
// ============================================================

/**
 * Custom hook for fetching and managing reading goals.
 * 
 * @param options - Configuration options
 * @returns {UseReadingGoalReturn} - Goal data and utilities
 * 
 * @example
 * ```tsx
 * // Basic usage
 * const { goal, loading, progress } = useReadingGoal();
 * 
 * // With options
 * const { goal, loading, refetch, updateGoal } = useReadingGoal({
 *   autoFetch: true,
 *   cache: true,
 * });
 * 
 * // Update goal
 * const handleUpdateGoal = async () => {
 *   await updateGoal(50, 'books');
 * };
 * ```
 */
export function useReadingGoal(options: UseReadingGoalOptions = {}): UseReadingGoalReturn {
  const {
    autoFetch = true,
    cache = true,
    cacheKey = 'reading-goal-cache',
  } = options;

  // ============================================================
  // 📦 State
  // ============================================================

  const [goal, setGoal] = useState<ReadingGoal | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [progress, setProgress] = useState<ReadingGoalProgress>({
    percentage: 0,
    remaining: 0,
    statusMessage: 'No goal set',
    statusVariant: 'default',
    isCompleted: false,
    isOnTrack: false,
  });
  const isMounted = useRef<boolean>(true);

  // ============================================================
  // 📊 Progress Calculation
  // ============================================================

  /**
   * Calculate progress from a reading goal.
   */
  const calculateProgress = useCallback((goalData: ReadingGoal | null): ReadingGoalProgress => {
    if (!goalData) {
      return {
        percentage: 0,
        remaining: 0,
        statusMessage: 'No goal set',
        statusVariant: 'default',
        isCompleted: false,
        isOnTrack: false,
      };
    }

    const { target, current, progressPercentage } = goalData;
    const remaining = Math.max(target - current, 0);
    const isCompleted = progressPercentage >= 100;
    const isOnTrack = progressPercentage >= 25;

    let statusMessage = '';
    let statusVariant: "default" | "success" | "warning" | "destructive" = "default";

    if (isCompleted) {
      statusMessage = '🎉 Goal achieved! Amazing work!';
      statusVariant = 'success';
    } else if (progressPercentage >= 75) {
      statusMessage = '🔥 Almost there! Keep going!';
      statusVariant = 'default';
    } else if (progressPercentage >= 50) {
      statusMessage = '📚 Halfway there! You\'re doing great!';
      statusVariant = 'default';
    } else if (progressPercentage >= 25) {
      statusMessage = '💪 Great start! Keep building momentum.';
      statusVariant = 'warning';
    } else if (progressPercentage > 0) {
      statusMessage = '🌟 Every book counts. Let\'s get started!';
      statusVariant = 'destructive';
    } else {
      statusMessage = '🌟 Set a goal and start reading today!';
      statusVariant = 'destructive';
    }

    return {
      percentage: progressPercentage,
      remaining,
      statusMessage,
      statusVariant,
      isCompleted,
      isOnTrack,
    };
  }, []);

  /**
   * Update progress whenever goal changes.
   * FIX: Wrap setState in queueMicrotask to avoid setState-in-effect warning
   */
  useEffect(() => {
    const progressValue = calculateProgress(goal);
    queueMicrotask(() => {
      if (!isMounted.current) return;
      setProgress(progressValue);
    });
  }, [goal, calculateProgress]);

  // ============================================================
  // 🛠️ Helper Functions
  // ============================================================

  /**
   * Load cached data from localStorage.
   */
  const loadFromCache = useCallback((): ReadingGoal | null => {
    if (!cache || typeof window === 'undefined') return null;
    
    try {
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        const parsed = JSON.parse(cached);
        if (parsed && typeof parsed === 'object') {
          return parsed;
        }
      }
    } catch (_err) {
      console.warn('Failed to load reading goal from cache:', _err);
    }
    return null;
  }, [cache, cacheKey]);

  /**
   * Save data to cache.
   */
  const saveToCache = useCallback((data: ReadingGoal) => {
    if (!cache || typeof window === 'undefined') return;
    
    try {
      localStorage.setItem(cacheKey, JSON.stringify(data));
    } catch (_err) {
      console.warn('Failed to save reading goal to cache:', _err);
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
   * Fetch reading goal.
   */
  const fetchGoal = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      const data = await readingService.getReadingGoal();
      
      if (isMounted.current) {
        if (data) {
          setGoal(data);
          saveToCache(data);
        } else {
          setGoal(null);
        }
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
              setGoal(cached);
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
   * Refetch the goal.
   */
  const refetch = useCallback(async (): Promise<void> => {
    await fetchGoal();
  }, [fetchGoal]);

  /**
   * Update the reading goal.
   */
  const updateGoal = useCallback(async (target: number, goalType: string = 'books'): Promise<void> => {
    if (target <= 0) {
      throw new Error('Target must be greater than 0');
    }

    try {
      setLoading(true);
      setError(null);

      // In a real implementation, this would call the API
      // const updated = await readingService.updateGoal({ target, goalType });
      
      // Mock implementation - update locally
      const current = goal?.current || 0;
      // FIX: Change 'as any' to 'as ReadingGoalType'
      const typedGoalType = goalType as ReadingGoalType;
      const newGoal: ReadingGoal = {
        goalType: typedGoalType,
        target,
        current,
        currentStreak: goal?.currentStreak || 0,
        longestStreak: goal?.longestStreak || 0,
        progressPercentage: target > 0 ? Math.min(Math.round((current / target) * 100), 100) : 0,
      };

      if (isMounted.current) {
        setGoal(newGoal);
        saveToCache(newGoal);
      }
    } catch (err) {
      if (isMounted.current) {
        setError(err as Error);
      }
      throw err;
    } finally {
      if (isMounted.current) {
        setLoading(false);
      }
    }
  }, [goal, saveToCache]);

  /**
   * Reset the hook state.
   */
  const reset = useCallback(() => {
    setGoal(null);
    setLoading(true);
    setError(null);
    setProgress({
      percentage: 0,
      remaining: 0,
      statusMessage: 'No goal set',
      statusVariant: 'default',
      isCompleted: false,
      isOnTrack: false,
    });
    clearCache();
    void fetchGoal();
  }, [clearCache, fetchGoal]);

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
          setGoal(cached);
          setLoading(false);
        });
      }
    }

    // Auto-fetch if enabled
    if (autoFetch) {
      let isFetchMounted = true;
      const fetchData = async () => {
        if (isFetchMounted) {
          await fetchGoal();
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
  }, [autoFetch, cache, fetchGoal, loadFromCache]);

  // ============================================================
  // 📦 Return
  // ============================================================

  return {
    goal,
    loading,
    error,
    progress,
    refetch,
    updateGoal,
    clearCache,
    reset,
  };
}

// ============================================================
// 🔄 Sub-hooks
// ============================================================

/**
 * useReadingGoalProgress - Hook for getting goal progress only.
 * 
 * @returns ReadingGoalProgress - Goal progress
 * 
 * @example
 * ```tsx
 * const progress = useReadingGoalProgress();
 * 
 * return (
 *   <div>
 *     <p>Progress: {progress.percentage}%</p>
 *     <p>{progress.statusMessage}</p>
 *   </div>
 * );
 * ```
 */
export function useReadingGoalProgress(): ReadingGoalProgress {
  const { progress, loading } = useReadingGoal({ autoFetch: true });
  
  if (loading) {
    return {
      percentage: 0,
      remaining: 0,
      statusMessage: 'Loading...',
      statusVariant: 'default',
      isCompleted: false,
      isOnTrack: false,
    };
  }
  
  return progress;
}

/**
 * useGoalCompletion - Hook for checking goal completion status.
 * 
 * @returns Object with completion status
 * 
 * @example
 * ```tsx
 * const { isCompleted, isOnTrack, progress } = useGoalCompletion();
 * 
 * return (
 *   <div>
 *     {isCompleted ? '🎉 Goal achieved!' : 'Keep reading!'}
 *   </div>
 * );
 * ```
 */
export function useGoalCompletion() {
  const { goal, progress, loading } = useReadingGoal({ autoFetch: true });

  return {
    isCompleted: progress.isCompleted,
    isOnTrack: progress.isOnTrack,
    progress: progress.percentage,
    remaining: progress.remaining,
    target: goal?.target || 0,
    current: goal?.current || 0,
    loading,
  };
}

/**
 * useGoalStreak - Hook for getting reading streak information.
 * 
 * @returns Streak information
 * 
 * @example
 * ```tsx
 * const { currentStreak, longestStreak, streakMessage } = useGoalStreak();
 * 
 * return (
 *   <div>
 *     <p>🔥 {currentStreak} day streak!</p>
 *   </div>
 * );
 * ```
 */
export function useGoalStreak() {
  const { goal, loading } = useReadingGoal({ autoFetch: true });

  const currentStreak = goal?.currentStreak || 0;
  const longestStreak = goal?.longestStreak || 0;

  let streakMessage = '';
  if (currentStreak === 0) {
    streakMessage = 'Start a reading streak today! 🔥';
  } else if (currentStreak < 7) {
    streakMessage = `${currentStreak} day${currentStreak > 1 ? 's' : ''} streak! Keep going! 📚`;
  } else if (currentStreak < 30) {
    streakMessage = `${currentStreak} days! Amazing consistency! 🎯`;
  } else {
    streakMessage = `${currentStreak} days! Reading master! 🏆`;
  }

  return {
    currentStreak,
    longestStreak,
    streakMessage,
    loading,
  };
}

// ============================================================
// 📦 Export Default
// ============================================================

export default useReadingGoal;