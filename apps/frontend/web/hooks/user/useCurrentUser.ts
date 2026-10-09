/**
 * ================================================================
 * 👤 useCurrentUser Hook
 * ================================================================
 *
 * A custom React hook for fetching and managing the current authenticated user.
 * 
 * Features:
 * - Fetches current user on mount
 * - Handles loading and error states
 * - Provides user profile management
 * - Offers user preferences and settings management
 * - Caches user data
 * - Provides user statistics and utilities
 * 
 * @example
 * ```tsx
 * const { user, loading, updateProfile, updatePreferences } = useCurrentUser();
 * 
 * if (loading) return <LoadingSpinner />;
 * if (error) return <ErrorMessage error={error} />;
 * 
 * return (
 *   <div>
 *     <h1>Welcome, {user?.fullName}</h1>
 *     <button onClick={() => updateProfile({ fullName: "John Doe" })}>
 *       Update Profile
 *     </button>
 *   </div>
 * );
 * ```
 * ================================================================
 */

import { useEffect, useState, useCallback, useRef, useMemo } from "react";

import { userService } from "@/lib/services";
import type { 
  CurrentUser, 
  UserPreferences, 
  UserSettings, 
  UpdateUserData 
} from "@/lib/types";

// ============================================================
// 📋 Types
// ============================================================

interface UseCurrentUserOptions {
  /** Automatically fetch on mount (default: true) */
  autoFetch?: boolean;
  
  /** Enable caching (default: true) */
  cache?: boolean;
  
  /** Cache key (default: 'current-user-cache') */
  cacheKey?: string;
  
  /** Cache expiration in milliseconds (default: 5 minutes) */
  cacheExpiration?: number;
}

interface UserStatistics {
  /** Books completed */
  booksCompleted: number;
  
  /** Books in progress */
  booksInProgress: number;
  
  /** Books saved to library */
  booksSaved: number;
  
  /** Total pages read */
  totalPagesRead: number;
  
  /** Current reading streak */
  currentReadingStreak: number;
  
  /** Longest reading streak achieved */
  longestReadingStreak: number;
  
  /** Total reading time in minutes */
  totalReadingTime: number;
  
  /** Average rating given */
  averageRating: number;
  
  /** Books abandoned */
  booksAbandoned: number;
  
  /** Most active month */
  mostActiveMonth: string;
  
  /** Reading level */
  readingLevel: "beginner" | "intermediate" | "advanced" | "expert";
  
  /** Reading level label */
  readingLevelLabel: string;
  
  /** Profile completion percentage */
  profileCompletion: number;
}

interface UseCurrentUserReturn {
  /** Current user data */
  user: CurrentUser | null;
  
  /** Whether data is currently loading */
  loading: boolean;
  
  /** Error object if request failed */
  error: Error | null;
  
  /** User statistics */
  stats: UserStatistics;
  
  /** User display name */
  displayName: string;
  
  /** User initials */
  initials: string;
  
  /** Update user profile */
  updateProfile: (data: Partial<UpdateUserData>) => Promise<CurrentUser>;
  
  /** Update user preferences */
  updatePreferences: (preferences: Partial<UserPreferences>) => Promise<CurrentUser>;
  
  /** Update user settings */
  updateSettings: (settings: Partial<UserSettings>) => Promise<CurrentUser>;
  
  /** Update user avatar */
  updateAvatar: (avatarUrl: string) => Promise<CurrentUser>;
  
  /** Refresh user data */
  refresh: () => Promise<void>;
  
  /** Clear cache */
  clearCache: () => void;
  
  /** Reset hook state */
  reset: () => void;
  
  /** Get formatted reading time */
  getReadingTimeFormatted: () => string;
  
  /** Get streak message */
  getStreakMessage: () => string;
  
  /** Check if user is authenticated */
  isAuthenticated: boolean;
  
  /** Check if user has reading streak */
  hasReadingStreak: boolean;
}

// ============================================================
// 🔧 Hook Implementation
// ============================================================

/**
 * Custom hook for fetching and managing the current user.
 * 
 * @param options - Configuration options
 * @returns {UseCurrentUserReturn} - User data and utilities
 * 
 * @example
 * ```tsx
 * // Basic usage
 * const { user, loading, stats } = useCurrentUser();
 * 
 * // With options
 * const { user, loading, refresh, updateProfile } = useCurrentUser({
 *   autoFetch: true,
 *   cache: true,
 *   cacheExpiration: 60000,
 * });
 * 
 * // Update profile
 * const handleUpdate = async () => {
 *   await updateProfile({ fullName: "John Doe" });
 * };
 * ```
 */
export function useCurrentUser(options: UseCurrentUserOptions = {}): UseCurrentUserReturn {
  const {
    autoFetch = true,
    cache = true,
    cacheKey = 'current-user-cache',
    cacheExpiration = 5 * 60 * 1000, // 5 minutes
  } = options;

  // ============================================================
  // 📦 State
  // ============================================================

  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const isMounted = useRef<boolean>(true);

  // ============================================================
  // 📊 Derived State
  // ============================================================

  const isAuthenticated = useMemo(() => {
    return user !== null && user.isActive !== false;
  }, [user]);

  const displayName = useMemo(() => {
    return user?.fullName || user?.username || "User";
  }, [user]);

  const initials = useMemo(() => {
    const name = displayName;
    const parts = name.split(" ");
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  }, [displayName]);

  const hasReadingStreak = useMemo(() => {
    return (user?.stats?.currentReadingStreak || 0) > 0;
  }, [user]);

  // ============================================================
  // 📊 Statistics
  // ============================================================

  const stats: UserStatistics = useMemo(() => {
    if (!user) {
      return {
        booksCompleted: 0,
        booksInProgress: 0,
        booksSaved: 0,
        totalPagesRead: 0,
        currentReadingStreak: 0,
        longestReadingStreak: 0,
        totalReadingTime: 0,
        averageRating: 0,
        booksAbandoned: 0,
        mostActiveMonth: "N/A",
        readingLevel: "beginner",
        readingLevelLabel: "📖 Beginner Reader",
        profileCompletion: 0,
      };
    }

    const books = user.stats?.booksCompleted || 0;
    let readingLevel: "beginner" | "intermediate" | "advanced" | "expert" = "beginner";
    
    if (books >= 60) readingLevel = "expert";
    else if (books >= 30) readingLevel = "advanced";
    else if (books >= 10) readingLevel = "intermediate";
    else readingLevel = "beginner";

    const levelLabels = {
      beginner: "📖 Beginner Reader",
      intermediate: "📚 Intermediate Reader",
      advanced: "🏆 Advanced Reader",
      expert: "👑 Expert Reader",
    };

    // Calculate profile completion
    let profileFields = 0;
    const totalFields = 6;
    if (user.id) profileFields++;
    if (user.username) profileFields++;
    if (user.email) profileFields++;
    if (user.fullName) profileFields++;
    if (user.avatar) profileFields++;
    if (user.preferences?.favoriteGenres?.length) profileFields++;
    const profileCompletion = Math.round((profileFields / totalFields) * 100);

    return {
      booksCompleted: user.stats?.booksCompleted || 0,
      booksInProgress: user.stats?.booksInProgress || 0,
      booksSaved: user.stats?.booksSaved || 0,
      totalPagesRead: user.stats?.totalPagesRead || 0,
      currentReadingStreak: user.stats?.currentReadingStreak || 0,
      longestReadingStreak: user.stats?.longestReadingStreak || 0,
      totalReadingTime: user.stats?.totalReadingTime || 0,
      averageRating: user.stats?.averageRating || 0,
      booksAbandoned: user.stats?.booksAbandoned || 0,
      mostActiveMonth: user.stats?.mostActiveMonth || "N/A",
      readingLevel,
      readingLevelLabel: levelLabels[readingLevel],
      profileCompletion,
    };
  }, [user]);

  // ============================================================
  // 🛠️ Helper Functions
  // ============================================================

  /**
   * Load user from cache.
   */
  const loadFromCache = useCallback((): CurrentUser | null => {
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
      console.warn('Failed to load user from cache:', _err);
    }
    return null;
  }, [cache, cacheKey, cacheExpiration]);

  /**
   * Save user to cache.
   */
  const saveToCache = useCallback((data: CurrentUser) => {
    if (!cache || typeof window === 'undefined') return;
    
    try {
      localStorage.setItem(cacheKey, JSON.stringify(data));
      localStorage.setItem(`${cacheKey}-timestamp`, Date.now().toString());
    } catch (_err) {
      console.warn('Failed to save user to cache:', _err);
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
   * Fetch user.
   */
  const fetchUser = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      const data = await userService.getCurrentUser();
      
      if (isMounted.current) {
        setUser(data);
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
              setUser(cached);
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
   * Refresh user data.
   */
  const refresh = useCallback(async (): Promise<void> => {
    await fetchUser();
  }, [fetchUser]);

  /**
   * Update user profile.
   */
  const updateProfile = useCallback(async (data: Partial<UpdateUserData>): Promise<CurrentUser> => {
    try {
      const updated = await userService.updateProfile(data);
      if (isMounted.current) {
        setUser(updated);
        saveToCache(updated);
      }
      return updated;
    } catch (err) {
      const error = err as Error;
      setError(error);
      throw error;
    }
  }, [saveToCache]);

  /**
   * Update user preferences.
   */
  const updatePreferences = useCallback(async (preferences: Partial<UserPreferences>): Promise<CurrentUser> => {
    try {
      const updated = await userService.updatePreferences(preferences);
      if (isMounted.current) {
        setUser(updated);
        saveToCache(updated);
      }
      return updated;
    } catch (err) {
      const error = err as Error;
      setError(error);
      throw error;
    }
  }, [saveToCache]);

  /**
   * Update user settings.
   */
  const updateSettings = useCallback(async (settings: Partial<UserSettings>): Promise<CurrentUser> => {
    try {
      const updated = await userService.updateSettings(settings);
      if (isMounted.current) {
        setUser(updated);
        saveToCache(updated);
      }
      return updated;
    } catch (err) {
      const error = err as Error;
      setError(error);
      throw error;
    }
  }, [saveToCache]);

  /**
   * Update user avatar.
   */
  const updateAvatar = useCallback(async (avatarUrl: string): Promise<CurrentUser> => {
    try {
      const updated = await userService.updateAvatar(avatarUrl);
      if (isMounted.current) {
        setUser(updated);
        saveToCache(updated);
      }
      return updated;
    } catch (err) {
      const error = err as Error;
      setError(error);
      throw error;
    }
  }, [saveToCache]);

  /**
   * Reset hook state.
   */
  const reset = useCallback(() => {
    setUser(null);
    setLoading(true);
    setError(null);
    clearCache();
    void fetchUser();
  }, [clearCache, fetchUser]);

  /**
   * Get formatted reading time.
   */
  const getReadingTimeFormatted = useCallback((): string => {
    const minutes = user?.stats?.totalReadingTime || 0;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    if (hours === 0) return `${remainingMinutes}m`;
    if (remainingMinutes === 0) return `${hours}h`;
    return `${hours}h ${remainingMinutes}m`;
  }, [user]);

  /**
   * Get streak message.
   */
  const getStreakMessage = useCallback((): string => {
    const streak = user?.stats?.currentReadingStreak || 0;
    if (streak === 0) return "Start a reading streak today! 🔥";
    if (streak < 7) return `${streak} day${streak > 1 ? "s" : ""} streak! Keep going! 📚`;
    if (streak < 30) return `${streak} days! Amazing consistency! 🎯`;
    return `${streak} days! Reading master! 🏆`;
  }, [user]);

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
          setUser(cached);
          setLoading(false);
        });
      }
    }

    // Auto-fetch if enabled
    if (autoFetch) {
      let isFetchMounted = true;
      const fetchData = async () => {
        if (isFetchMounted) {
          await fetchUser();
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
  }, [autoFetch, cache, fetchUser, loadFromCache]);

  // ============================================================
  // 📦 Return
  // ============================================================

  return {
    user,
    loading,
    error,
    stats,
    displayName,
    initials,
    updateProfile,
    updatePreferences,
    updateSettings,
    updateAvatar,
    refresh,
    clearCache,
    reset,
    getReadingTimeFormatted,
    getStreakMessage,
    isAuthenticated,
    hasReadingStreak,
  };
}

// ============================================================
// 🔄 Sub-hooks
// ============================================================

/**
 * useUserStats - Hook for getting user statistics only.
 * 
 * @returns UserStatistics - User statistics
 * 
 * @example
 * ```tsx
 * const stats = useUserStats();
 * 
 * return (
 *   <div>
 *     <p>📚 Books completed: {stats.booksCompleted}</p>
 *     <p>🔥 Streak: {stats.currentReadingStreak} days</p>
 *   </div>
 * );
 * ```
 */
export function useUserStats(): UserStatistics {
  const { stats, loading } = useCurrentUser({ autoFetch: true });
  
  if (loading) {
    return {
      booksCompleted: 0,
      booksInProgress: 0,
      booksSaved: 0,
      totalPagesRead: 0,
      currentReadingStreak: 0,
      longestReadingStreak: 0,
      totalReadingTime: 0,
      averageRating: 0,
      booksAbandoned: 0,
      mostActiveMonth: "N/A",
      readingLevel: "beginner",
      readingLevelLabel: "📖 Beginner Reader",
      profileCompletion: 0,
    };
  }
  
  return stats;
}

/**
 * useUserDisplay - Hook for getting user display information.
 * 
 * @returns User display information
 * 
 * @example
 * ```tsx
 * const { displayName, initials, avatar } = useUserDisplay();
 * 
 * return (
 *   <div>
 *     <Avatar src={avatar} fallback={initials} />
 *     <h2>{displayName}</h2>
 *   </div>
 * );
 * ```
 */
export function useUserDisplay() {
  const { user, displayName, initials, loading } = useCurrentUser({ autoFetch: true });
  
  return {
    displayName,
    initials,
    avatar: user?.avatar,
    email: user?.email,
    username: user?.username,
    loading,
  };
}

// ============================================================
// 📦 Export Default
// ============================================================

export default useCurrentUser;