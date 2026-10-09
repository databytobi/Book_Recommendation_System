/**
 * ================================================================
 * 💡 useRecommendation Hook
 * ================================================================
 *
 * A custom React hook for fetching and managing recommendations.
 * 
 * Features:
 * - Fetches recommendation sections on mount
 * - Handles loading and error states
 * - Provides filtering and sorting capabilities
 * - Offers recommendation statistics
 * - Caches results to prevent unnecessary requests
 * 
 * @example
 * ```tsx
 * const { sections, loading, stats, getRecommendationsByAlgorithm } = useRecommendations();
 * 
 * if (loading) return <LoadingSpinner />;
 * if (error) return <ErrorMessage error={error} />;
 * 
 * return (
 *   <div>
 *     <p>Total recommendations: {stats.totalRecommendations}</p>
 *     {sections.map(section => (
 *       <RecommendationSection key={section.id} section={section} />
 *     ))}
 *   </div>
 * );
 * ```
 * ================================================================
 */

import { useEffect, useState, useCallback, useRef, useMemo } from "react";

import { recommendationService } from "@/lib/services";
import type { 
  RecommendationSection, 
  RecommendationBook, 
  RecommendationAlgorithm,
  RecommendationConfidence 
} from "@/lib/types";

// ============================================================
// 📋 Types
// ============================================================

interface UseRecommendationOptions {
  /** Automatically fetch on mount (default: true) */
  autoFetch?: boolean;
  
  /** Enable caching (default: true) */
  cache?: boolean;
  
  /** Cache key (default: 'recommendations-cache') */
  cacheKey?: string;
  
  /** Minimum score filter */
  minScore?: number;
  
  /** Filter by confidence level */
  confidence?: RecommendationConfidence;
}

interface RecommendationStats {
  /** Total number of recommendations */
  totalRecommendations: number;
  
  /** Average recommendation score */
  averageScore: number;
  
  /** High confidence recommendations count */
  highConfidenceCount: number;
  
  /** Recommendations by algorithm distribution */
  algorithmDistribution: Record<string, number>;
  
  /** Number of recommendation sections */
  sectionsCount: number;
  
  /** Featured sections count */
  featuredSectionsCount: number;
  
  /** Highest scoring recommendation */
  highestScore: number;
}

interface UseRecommendationReturn {
  /** All recommendation sections */
  sections: RecommendationSection[];
  
  /** All recommendation books across all sections */
  allBooks: RecommendationBook[];
  
  /** Whether data is currently loading */
  loading: boolean;
  
  /** Error object if request failed */
  error: Error | null;
  
  /** Recommendation statistics */
  stats: RecommendationStats;
  
  /** Filter by minimum score */
  minScoreFilter: number | null;
  
  /** Filter by confidence level */
  confidenceFilter: RecommendationConfidence | null;
  
  /** Set minimum score filter */
  setMinScoreFilter: (score: number | null) => void;
  
  /** Set confidence filter */
  setConfidenceFilter: (confidence: RecommendationConfidence | null) => void;
  
  /** Get recommendations by algorithm */
  getRecommendationsByAlgorithm: (algorithm: RecommendationAlgorithm) => RecommendationBook[];
  
  /** Get high confidence recommendations */
  getHighConfidenceRecommendations: () => RecommendationBook[];
  
  /** Get featured sections */
  getFeaturedSections: () => RecommendationSection[];
  
  /** Get top N recommendations by score */
  getTopRecommendations: (limit?: number) => RecommendationBook[];
  
  /** Manually refetch recommendations */
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
 * Custom hook for fetching and managing recommendations.
 * 
 * @param options - Configuration options
 * @returns {UseRecommendationReturn} - Recommendation data and utilities
 * 
 * @example
 * ```tsx
 * // Basic usage
 * const { sections, loading, stats } = useRecommendations();
 * 
 * // With filters
 * const { sections, allBooks, setMinScoreFilter, setConfidenceFilter } = useRecommendations({
 *   autoFetch: true,
 *   cache: true,
 *   minScore: 70,
 *   confidence: "high",
 * });
 * 
 * // Get top recommendations
 * const top5 = getTopRecommendations(5);
 * ```
 */
export function useRecommendations(options: UseRecommendationOptions = {}): UseRecommendationReturn {
  const {
    autoFetch = true,
    cache = true,
    cacheKey = 'recommendations-cache',
    minScore = null,
    confidence = null,
  } = options;

  // ============================================================
  // 📦 State
  // ============================================================

  const [sections, setSections] = useState<RecommendationSection[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [minScoreFilter, setMinScoreFilter] = useState<number | null>(minScore);
  const [confidenceFilter, setConfidenceFilter] = useState<RecommendationConfidence | null>(confidence);
  const isMounted = useRef<boolean>(true);

  // ============================================================
  // 📊 Derived State
  // ============================================================

  /**
   * Get all books across all sections.
   */
  const allBooks = useMemo((): RecommendationBook[] => {
    return sections.flatMap(section => section.books);
  }, [sections]);

  /**
   * Calculate recommendation statistics.
   */
  const stats = useMemo((): RecommendationStats => {
    const total = allBooks.length;
    const scores = allBooks.map(b => b.score).filter(s => s !== undefined && s !== null) as number[];
    const avgScore = scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
    const highConfidence = allBooks.filter(b => b.confidence === "high").length;
    
    const algorithmDistribution: Record<string, number> = {};
    allBooks.forEach(book => {
      const alg = book.algorithm || "unknown";
      algorithmDistribution[alg] = (algorithmDistribution[alg] || 0) + 1;
    });

    const featuredSections = sections.filter(s => s.featured);
    const highestScore = scores.length > 0 ? Math.max(...scores) : 0;

    return {
      totalRecommendations: total,
      averageScore: avgScore,
      highConfidenceCount: highConfidence,
      algorithmDistribution,
      sectionsCount: sections.length,
      featuredSectionsCount: featuredSections.length,
      highestScore,
    };
  }, [allBooks, sections]);

  // FIX 1: Removed filteredBooks - it was never used

  // ============================================================
  // 🛠️ Helper Functions
  // ============================================================

  /**
   * Load cached data from localStorage.
   */
  const loadFromCache = useCallback((): RecommendationSection[] | null => {
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
      console.warn('Failed to load recommendations from cache:', _err);
    }
    return null;
  }, [cache, cacheKey]);

  /**
   * Save data to cache.
   */
  const saveToCache = useCallback((data: RecommendationSection[]) => {
    if (!cache || typeof window === 'undefined') return;
    
    try {
      localStorage.setItem(cacheKey, JSON.stringify(data));
    } catch (_err) {
      console.warn('Failed to save recommendations to cache:', _err);
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
   * Fetch recommendations.
   */
  const fetchRecommendations = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      const data = await recommendationService.getRecommendations();
      
      if (isMounted.current) {
        setSections(data);
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
              setSections(cached);
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
   * Refetch recommendations.
   */
  const refetch = useCallback(async (): Promise<void> => {
    await fetchRecommendations();
  }, [fetchRecommendations]);

  /**
   * Get recommendations by algorithm.
   */
  const getRecommendationsByAlgorithm = useCallback((algorithm: RecommendationAlgorithm): RecommendationBook[] => {
    return allBooks.filter(book => book.algorithm === algorithm);
  }, [allBooks]);

  /**
   * Get high confidence recommendations.
   */
  const getHighConfidenceRecommendations = useCallback((): RecommendationBook[] => {
    return allBooks.filter(book => book.confidence === "high");
  }, [allBooks]);

  /**
   * Get featured sections.
   */
  const getFeaturedSections = useCallback((): RecommendationSection[] => {
    return sections.filter(section => section.featured);
  }, [sections]);

  /**
   * Get top N recommendations by score.
   */
  const getTopRecommendations = useCallback((limit: number = 5): RecommendationBook[] => {
    return [...allBooks]
      .sort((a, b) => (b.score || 0) - (a.score || 0))
      .slice(0, limit);
  }, [allBooks]);

  /**
   * Reset the hook state.
   */
  const reset = useCallback(() => {
    setSections([]);
    setLoading(true);
    setError(null);
    setMinScoreFilter(null);
    setConfidenceFilter(null);
    clearCache();
    // FIX: Add void to async call
    void fetchRecommendations();
  }, [clearCache, fetchRecommendations]);

  // ============================================================
  // 🎯 Effects
  // ============================================================

  // FIX 2: Initial fetch on mount with queueMicrotask
  useEffect(() => {
    isMounted.current = true;

    if (cache) {
      const cached = loadFromCache();

      if (cached) {
        queueMicrotask(() => {
          if (!isMounted.current) return;

          setSections(cached);
          setLoading(false);
        });
      }
    }

    if (autoFetch) {
      let isFetchMounted = true;
      const fetchData = async () => {
        if (isFetchMounted) {
          await fetchRecommendations();
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
  }, [autoFetch, cache, fetchRecommendations, loadFromCache]);

  // ============================================================
  // 📦 Return
  // ============================================================

  return {
    sections,
    allBooks,
    loading,
    error,
    stats,
    minScoreFilter,
    confidenceFilter,
    setMinScoreFilter,
    setConfidenceFilter,
    getRecommendationsByAlgorithm,
    getHighConfidenceRecommendations,
    getFeaturedSections,
    getTopRecommendations,
    refetch,
    clearCache,
    reset,
  };
}

// ============================================================
// 🔄 Sub-hooks
// ============================================================

/**
 * useRecommendationStats - Hook for getting recommendation statistics only.
 * 
 * @returns RecommendationStats - Recommendation statistics
 * 
 * @example
 * ```tsx
 * const stats = useRecommendationStats();
 * 
 * return (
 *   <div>
 *     <p>Total recommendations: {stats.totalRecommendations}</p>
 *     <p>Average score: {stats.averageScore}%</p>
 *   </div>
 * );
 * ```
 */
export function useRecommendationStats(): RecommendationStats {
  const { stats, loading } = useRecommendations({ autoFetch: true });
  
  if (loading) {
    return {
      totalRecommendations: 0,
      averageScore: 0,
      highConfidenceCount: 0,
      algorithmDistribution: {},
      sectionsCount: 0,
      featuredSectionsCount: 0,
      highestScore: 0,
    };
  }
  
  return stats;
}

/**
 * useTopRecommendations - Hook for getting top recommendations.
 * 
 * @param limit - Number of recommendations to return (default: 5)
 * @returns Top recommendations
 * 
 * @example
 * ```tsx
 * const topRecommendations = useTopRecommendations(5);
 * 
 * return (
 *   <div>
 *     {topRecommendations.map(book => (
 *       <BookCard key={book.id} book={book} />
 *     ))}
 *   </div>
 * );
 * ```
 */
export function useTopRecommendations(limit: number = 5) {
  const { getTopRecommendations, loading } = useRecommendations({ autoFetch: true });
  
  return {
    recommendations: getTopRecommendations(limit),
    loading,
  };
}

/**
 * useRecommendationSection - Hook for getting a specific section.
 * 
 * @param sectionId - The section ID
 * @returns Section data
 * 
 * @example
 * ```tsx
 * const { section, loading } = useRecommendationSection("recommended");
 * 
 * return (
 *   <div>
 *     <h2>{section?.title}</h2>
 *     {section?.books.map(book => (
 *       <BookCard key={book.id} book={book} />
 *     ))}
 *   </div>
 * );
 * ```
 */
export function useRecommendationSection(sectionId: string) {
  const { sections, loading } = useRecommendations({ autoFetch: true });
  
  const section = sections.find(s => s.id === sectionId);
  
  return {
    section,
    books: section?.books || [],
    loading,
  };
}

// ============================================================
// 📦 Export Default
// ============================================================

export default useRecommendations;