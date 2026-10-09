/**
 * ================================================================
 * 🔍 useSearch Hook
 * ================================================================
 *
 * A custom React hook for searching books with advanced features.
 * 
 * Features:
 * - Search books with query and filters
 * - Handles loading and error states
 * - Provides search history management
 * - Offers debounced search
 * - Caches search results
 * - Provides search statistics
 * 
 * @example
 * ```tsx
 * const { results, loading, search, searchHistory, clearHistory } = useSearch();
 * 
 * const handleSearch = (query: string) => {
 *   search(query);
 * };
 * 
 * return (
 *   <div>
 *     <input onChange={(e) => search(e.target.value)} />
 *     {loading ? <LoadingSpinner /> : <SearchResults results={results} />}
 *     <SearchHistory history={searchHistory} onClear={clearHistory} />
 *   </div>
 * );
 * ```
 * ================================================================
 */

import { useState, useCallback, useRef, useEffect, useMemo } from "react";
import { searchService } from "@/lib/services";
import type { 
  SearchResponse, 
  SearchFilters, 
  SearchHistoryItem, 
  PopularSearchItem 
} from "@/lib/types";

// ============================================================
// 📋 Types
// ============================================================

interface UseSearchOptions {
  /** Automatically search on mount (default: false) */
  autoSearch?: boolean;
  
  /** Initial search query */
  initialQuery?: string;
  
  /** Initial filters */
  initialFilters?: Partial<SearchFilters>;
  
  /** Enable debouncing (default: true) */
  debounce?: boolean;
  
  /** Debounce delay in milliseconds (default: 300) */
  debounceDelay?: number;
  
  /** Enable caching (default: true) */
  cache?: boolean;
  
  /** Maximum cache size (default: 20) */
  maxCacheSize?: number;
  
  /** Minimum query length to trigger search (default: 2) */
  minQueryLength?: number;
}

interface SearchCacheEntry {
  query: string;
  response: SearchResponse;
  timestamp: number;
}

interface UseSearchReturn {
  /** Search results */
  results: SearchResponse | null;
  
  /** Whether data is currently loading */
  loading: boolean;
  
  /** Error object if request failed */
  error: Error | null;
  
  /** Current search query */
  query: string;
  
  /** Current search filters */
  filters: Partial<SearchFilters>;
  
  /** Search history */
  searchHistory: SearchHistoryItem[];
  
  /** Perform a search */
  search: (query: string, filters?: Partial<SearchFilters>) => Promise<void>;
  
  /** Clear search results */
  clearResults: () => void;
  
  /** Clear search history */
  clearHistory: () => Promise<void>;
  
  /** Remove a specific search from history */
  removeFromHistory: (id: string) => Promise<boolean>;
  
  /** Update filters */
  setFilters: (filters: Partial<SearchFilters>) => void;
  
  /** Reset all state */
  reset: () => void;
  
  /** Get popular searches */
  getPopularSearches: () => Promise<PopularSearchItem[]>;
  
  /** Check if search has results */
  hasResults: boolean;
  
  /** Total number of results */
  totalResults: number;
  
  /** Pagination info */
  pagination: {
    currentPage: number;
    totalPages: number;
    resultsPerPage: number;
  };
}

// ============================================================
// 🔧 Hook Implementation
// ============================================================

/**
 * Custom hook for searching books.
 * 
 * @param options - Configuration options
 * @returns {UseSearchReturn} - Search data and utilities
 * 
 * @example
 * ```tsx
 * // Basic usage
 * const { results, loading, search } = useSearch();
 * 
 * // With debounce
 * const { results, loading, search } = useSearch({
 *   debounce: true,
 *   debounceDelay: 500,
 *   minQueryLength: 3,
 * });
 * 
 * // With filters
 * const { results, loading, search, setFilters } = useSearch({
 *   initialFilters: { minimumRating: 4.0 }
 * });
 * ```
 */
export function useSearch(options: UseSearchOptions = {}): UseSearchReturn {
  const {
    autoSearch = false,
    initialQuery = "",
    initialFilters = {},
    debounce = true,
    debounceDelay = 300,
    cache = true,
    maxCacheSize = 20,
    minQueryLength = 2,
  } = options;

  // ============================================================
  // 📦 State
  // ============================================================

  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [query, setQuery] = useState<string>(initialQuery);
  const [filters, setFiltersState] = useState<Partial<SearchFilters>>(initialFilters);
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([]);
  const [popularSearches, setPopularSearches] = useState<PopularSearchItem[]>([]);
  const [cacheStore, setCacheStore] = useState<SearchCacheEntry[]>([]);
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);
  const isMounted = useRef<boolean>(true);

  // ============================================================
  // 📊 Derived State
  // ============================================================

  const hasResults = useMemo(() => {
    return results !== null && results.totalResults > 0;
  }, [results]);

  const totalResults = useMemo(() => {
    return results?.totalResults || 0;
  }, [results]);

  const pagination = useMemo(() => {
    return {
      currentPage: results?.page || 1,
      totalPages: results?.totalPages || 0,
      resultsPerPage: results?.limit || 20,
    };
  }, [results]);

  // ============================================================
  // 🛠️ Helper Functions
  // ============================================================

  /**
   * Get cache key for a query and filters.
   */
  const getCacheKey = useCallback((searchQuery: string, searchFilters?: Partial<SearchFilters>): string => {
    const filterString = searchFilters ? JSON.stringify(searchFilters) : '';
    return `${searchQuery}|${filterString}`;
  }, []);

  /**
   * Get cached response if available.
   */
  const getCachedResponse = useCallback((searchQuery: string, searchFilters?: Partial<SearchFilters>): SearchResponse | null => {
    if (!cache) return null;
    
    const key = getCacheKey(searchQuery, searchFilters);
    const cached = cacheStore.find(entry => {
      const entryKey = getCacheKey(entry.query, searchFilters);
      return entryKey === key;
    });
    
    if (cached) {
      // Check if cache is still valid (5 minutes)
      const age = Date.now() - cached.timestamp;
      if (age < 5 * 60 * 1000) {
        return cached.response;
      }
    }
    return null;
  }, [cache, cacheStore, getCacheKey]);

  /**
   * Save response to cache.
   */
  const saveToCache = useCallback((searchQuery: string, response: SearchResponse, searchFilters?: Partial<SearchFilters>) => {
    if (!cache) return;
    
    const key = getCacheKey(searchQuery, searchFilters);
    const entry: SearchCacheEntry = {
      query: searchQuery,
      response,
      timestamp: Date.now(),
    };
    
    setCacheStore(prev => {
      const filtered = prev.filter(e => getCacheKey(e.query, searchFilters) !== key);
      const updated = [entry, ...filtered];
      // Limit cache size
      if (updated.length > maxCacheSize) {
        updated.pop();
      }
      return updated;
    });
  }, [cache, maxCacheSize, getCacheKey]);

  /**
   * Load search history.
   */
  const loadSearchHistory = useCallback(async () => {
    try {
      const history = await searchService.getSearchHistory();
      if (isMounted.current) {
        setSearchHistory(history);
      }
    } catch (err) {
      console.warn('Failed to load search history:', err);
    }
  }, []);

  /**
   * Load popular searches.
   */
  const loadPopularSearches = useCallback(async () => {
    try {
      const popular = await searchService.getPopularSearches();
      if (isMounted.current) {
        setPopularSearches(popular);
      }
    } catch (err) {
      console.warn('Failed to load popular searches:', err);
    }
  }, []);

  /**
   * Perform search.
   */
  const performSearch = useCallback(async (searchQuery: string, searchFilters?: Partial<SearchFilters>) => {
    // Validate query length
    if (searchQuery.length < minQueryLength) {
      setResults(null);
      setError(null);
      return;
    }

    // Check cache
    const cached = getCachedResponse(searchQuery, searchFilters);
    if (cached) {
      if (isMounted.current) {
        setResults(cached);
        setLoading(false);
      }
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await searchService.searchBooks(searchQuery, searchFilters);
      
      if (isMounted.current) {
        setResults(response);
        setQuery(searchQuery);
        saveToCache(searchQuery, response, searchFilters);
      }
    } catch (err) {
      if (isMounted.current) {
        setError(err as Error);
      }
    } finally {
      if (isMounted.current) {
        setLoading(false);
      }
    }
  }, [getCachedResponse, minQueryLength, saveToCache]);

  /**
   * Debounced search.
   */
  const search = useCallback(async (searchQuery: string, searchFilters?: Partial<SearchFilters>) => {
    // Clear any existing timer
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
      debounceTimer.current = null;
    }

    if (!debounce) {
      await performSearch(searchQuery, searchFilters);
      return;
    }

    // Debounce the search
    debounceTimer.current = setTimeout(async () => {
      await performSearch(searchQuery, searchFilters);
    }, debounceDelay);
  }, [debounce, debounceDelay, performSearch]);

  /**
   * Clear search results.
   */
  const clearResults = useCallback(() => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
      debounceTimer.current = null;
    }
    setResults(null);
    setQuery("");
  }, []);

  /**
   * Clear search history.
   */
  const clearHistory = useCallback(async () => {
    try {
      await searchService.clearSearchHistory();  // ✅ CORRECT - matches service
      if (isMounted.current) {
        setSearchHistory([]);
      }
    } catch (err) {
      console.warn('Failed to clear search history:', err);
    }
  }, []);

  /**
   * Remove a specific search from history.
   */
  const removeFromHistory = useCallback(async (id: string): Promise<boolean> => {
    try {
      await searchService.removeSearchTerm(id);  // ✅ CORRECT - matches service
      if (isMounted.current) {
        setSearchHistory(prev => prev.filter(item => item.id !== id));
      }
      return true;
    } catch (err) {
      console.warn('Failed to remove search term:', err);
      return false;
    }
  }, []);

  /**
   * Update filters.
   */
  const setFilters = useCallback((newFilters: Partial<SearchFilters>) => {
    setFiltersState(prev => ({ ...prev, ...newFilters }));
  }, []);

  /**
   * Get popular searches.
   */
  const getPopularSearches = useCallback(async (): Promise<PopularSearchItem[]> => {
    try {
      // Return cached popular searches if available
      if (popularSearches.length > 0) {
        return popularSearches;
      }
      
      // Otherwise fetch from service
      const popular = await searchService.getPopularSearches();
      if (isMounted.current) {
        setPopularSearches(popular);
      }
      return popular;
    } catch (err) {
      console.error('Failed to get popular searches:', err);
      return [];
    }
  }, [popularSearches]);

  /**
   * Reset all state.
   */
  const reset = useCallback(() => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
      debounceTimer.current = null;
    }
    setResults(null);
    setLoading(false);
    setError(null);
    setQuery("");
    setFiltersState({});
    setSearchHistory([]);
    setPopularSearches([]);
    setCacheStore([]);
  }, []);

  // ============================================================
  // 🎯 Effects
  // ============================================================

  useEffect(() => {
    isMounted.current = true;

    queueMicrotask(() => {
      void loadSearchHistory();
      void loadPopularSearches();

      if (autoSearch && initialQuery) {
        void performSearch(initialQuery);
      }
    });

    return () => {
      isMounted.current = false;

      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, [
    autoSearch,
    initialQuery,
    loadSearchHistory,
    loadPopularSearches,
    performSearch,
  ]);

  useEffect(() => {
    if (!(query && query.length >= minQueryLength)) return;

    queueMicrotask(() => {
      void performSearch(query, filters);
    });
  }, [filters, performSearch, query, minQueryLength]);

  // ============================================================
  // 📦 Return
  // ============================================================

  return {
    results,
    loading,
    error,
    query,
    filters,
    searchHistory,
    search,
    clearResults,
    clearHistory,
    removeFromHistory,
    setFilters,
    reset,
    getPopularSearches,
    hasResults,
    totalResults,
    pagination,
  };
}

// ============================================================
// 🔄 Sub-hooks
// ============================================================

/**
 * useDebouncedSearch - Hook for debounced search with auto-trigger.
 * 
 * @param initialQuery - Initial search query
 * @param delay - Debounce delay in milliseconds
 * @returns Search state and controls
 * 
 * @example
 * ```tsx
 * const { query, setQuery, results, loading } = useDebouncedSearch("", 500);
 * 
 * return (
 *   <div>
 *     <input value={query} onChange={(e) => setQuery(e.target.value)} />
 *     {loading ? <LoadingSpinner /> : <SearchResults results={results} />}
 *   </div>
 * );
 * ```
 */
export function useDebouncedSearch(initialQuery: string = "", delay: number = 500) {
  const [query, setQuery] = useState(initialQuery);
  const [debouncedQuery, setDebouncedQuery] = useState(initialQuery);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    timerRef.current = setTimeout(() => {
      setDebouncedQuery(query);
    }, delay);

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [query, delay]);

  const { results, loading, error, search } = useSearch({
    autoSearch: true,
    initialQuery: debouncedQuery,
    debounce: false,
  });

  return {
    query,
    setQuery,
    debouncedQuery,
    results,
    loading,
    error,
    search: (q: string) => search(q),
  };
}

/**
 * useSearchWithFilters - Hook for search with filter controls.
 * 
 * @param initialQuery - Initial search query
 * @param initialFilters - Initial filters
 * @returns Search state with filter controls
 * 
 * @example
 * ```tsx
 * const { query, setQuery, filters, setFilters, results, loading } = useSearchWithFilters();
 * 
 * return (
 *   <div>
 *     <input value={query} onChange={(e) => setQuery(e.target.value)} />
 *     <FilterControls filters={filters} onChange={setFilters} />
 *     <SearchResults results={results} loading={loading} />
 *   </div>
 * );
 * ```
 */
export function useSearchWithFilters(
  initialQuery: string = "",
  initialFilters: Partial<SearchFilters> = {}
) {
  const { results, loading, error, search, filters, setFilters, hasResults, totalResults } = useSearch({
    initialQuery,
    initialFilters,
    debounce: true,
    debounceDelay: 300,
  });

  const handleSearch = useCallback((query: string) => {
    search(query);
  }, [search]);

  return {
    query: initialQuery,
    setQuery: handleSearch,
    filters,
    setFilters,
    results,
    loading,
    error,
    hasResults,
    totalResults,
  };
}

// ============================================================
// 📦 Export Default
// ============================================================

export default useSearch;