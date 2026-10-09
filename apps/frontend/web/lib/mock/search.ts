/**
 * ================================================================
 * 🔍 Search Mock Data
 * ================================================================
 *
 * This file contains mock search data for development and testing.
 * It represents:
 * - Search history
 * - Popular searches
 * - Search responses
 * - Search functionality
 *
 * IMPORTANT: This is mock data and should be replaced with
 * real API data in production.
 * ================================================================
 */

import type {
  SearchHistoryItem,
  SearchResponse,
  SearchFilters,
  PopularSearchItem,
} from "@/lib/types";

// FIX: Removed unused 'searchBooksUtil' import
import { books } from "./books";

// ============================================================
// 📜 Search History
// ============================================================

/**
 * Mock search history for the current user.
 * Shows the user's recent search queries with timestamps.
 */
export const searchHistory: SearchHistoryItem[] = [
  {
    id: "search_1",
    query: "Atomic Habits",
    searchedAt: "2026-07-17T08:30:00Z",
    searchedAtDisplay: "Today, 8:30 AM",
    resultCount: 1,
  },
  {
    id: "search_2",
    query: "Fantasy",
    searchedAt: "2026-07-16T18:20:00Z",
    searchedAtDisplay: "Yesterday, 6:20 PM",
    resultCount: 3,
  },
  {
    id: "search_3",
    query: "Dune",
    searchedAt: "2026-07-15T21:10:00Z",
    searchedAtDisplay: "2 days ago, 9:10 PM",
    resultCount: 2,
  },
  {
    id: "search_4",
    query: "Self Development",
    searchedAt: "2026-07-14T14:45:00Z",
    searchedAtDisplay: "3 days ago, 2:45 PM",
    resultCount: 5,
  },
  {
    id: "search_5",
    query: "Science Fiction",
    searchedAt: "2026-07-12T10:00:00Z",
    searchedAtDisplay: "5 days ago, 10:00 AM",
    resultCount: 4,
  },
];

// ============================================================
// 🔥 Popular Searches
// ============================================================

/**
 * Mock popular searches across the platform.
 * Shows trending and frequently searched queries.
 */
export const popularSearches: PopularSearchItem[] = [
  {
    query: "Self Help",
    searchCount: 245,
    trend: "up",
    changePercentage: 12,
    category: "genre",
  },
  {
    query: "Fantasy",
    searchCount: 221,
    trend: "up",
    changePercentage: 8,
    category: "genre",
  },
  {
    query: "Science Fiction",
    searchCount: 198,
    trend: "neutral",
    changePercentage: 0,
    category: "genre",
  },
  {
    query: "Business",
    searchCount: 170,
    trend: "down",
    changePercentage: -5,
    category: "genre",
  },
  {
    query: "Atomic Habits",
    searchCount: 156,
    trend: "up",
    changePercentage: 15,
    category: "book",
  },
  {
    query: "James Clear",
    searchCount: 134,
    trend: "up",
    changePercentage: 10,
    category: "author",
  },
];

// ============================================================
// 📊 Search Response
// ============================================================

/**
 * Mock search filters available to users.
 */
export const defaultFilters: SearchFilters = {
  minimumRating: 4.0,
  language: "en",
  availableOnly: true,
};

/**
 * Mock search response for a specific query.
 */
export const mockSearchResponse: SearchResponse = {
  query: "Atomic",
  totalResults: 1,
  results: [
    {
      book: books[0],
      similarityScore: 0.99,
      highlights: ["<strong>Atomic</strong> Habits"],
    },
  ],
  filters: {
    minimumRating: 4.5,
    language: "en",
  },
  searchTimeMs: 245,
  suggestions: ["Atomic Habits", "Atomic Design", "Atom"],
  page: 1,
  limit: 20,
  totalPages: 1,
};

// ============================================================
// 🔄 Search Functions
// ============================================================

/**
 * Search books by query.
 * 
 * @param query - The search query string
 * @param filters - Optional search filters
 * @returns SearchResponse with matching books
 */
export function searchBooks(
  query: string,
  filters?: Partial<SearchFilters>
): SearchResponse {
  const normalized = query.toLowerCase().trim();
  
  if (!normalized) {
    return {
      query: normalized,
      totalResults: 0,
      results: [],
      searchTimeMs: 0,
      page: 1,
      limit: 20,
      totalPages: 0,
    };
  }

  const startTime = performance.now();

  // Filter books by title
  let results = books
    .filter((book) =>
      book.title.toLowerCase().includes(normalized)
    )
    .map((book) => ({
      book,
      similarityScore: 0.95 + Math.random() * 0.05,
      highlights: [`<strong>${book.title}</strong>`],
    }));

  // Apply filters if provided
  if (filters?.minimumRating) {
    results = results.filter(
      (result) => (result.book.rating || 0) >= (filters.minimumRating || 0)
    );
  }

  if (filters?.genre) {
    // Mock genre filtering - in real implementation, books would have genres
    results = results.filter((result) =>
      result.book.title.toLowerCase().includes(filters.genre!.toLowerCase())
    );
  }

  // Sort by similarity score
  results.sort((a, b) => (b.similarityScore || 0) - (a.similarityScore || 0));

  const searchTimeMs = Math.round(performance.now() - startTime);
  const totalResults = results.length;

  // Generate suggestions if no results or few results
  let suggestions: string[] | undefined;
  if (totalResults === 0) {
    suggestions = ["Try a different keyword", "Check your spelling"];
  } else if (totalResults < 3 && totalResults > 0) {
    suggestions = ["Try a broader search term"];
  }

  return {
    query: normalized,
    totalResults,
    results,
    filters: {
      ...defaultFilters,
      ...filters,
    },
    searchTimeMs,
    suggestions,
    page: 1,
    limit: 20,
    totalPages: Math.ceil(totalResults / 20),
  };
}

/**
 * Get search history for the current user.
 */
export function getSearchHistory(): SearchHistoryItem[] {
  return searchHistory;
}

/**
 * Get popular searches across the platform.
 */
export function getPopularSearches(): PopularSearchItem[] {
  return popularSearches;
}

/**
 * Get a search history item by ID.
 */
export function getSearchHistoryItem(id: string): SearchHistoryItem | undefined {
  return searchHistory.find((item) => item.id === id);
}

/**
 * Add a search to history.
 */
export function addSearchToHistory(query: string): SearchHistoryItem {
  const newItem: SearchHistoryItem = {
    id: `search_${Date.now()}`,
    query,
    searchedAt: new Date().toISOString(),
    searchedAtDisplay: "Just now",
    resultCount: 0,
  };
  searchHistory.unshift(newItem);
  return newItem;
}

/**
 * Clear search history.
 */
export function clearSearchHistory(): void {
  searchHistory.length = 0;
}

/**
 * Remove a specific search from history.
 */
export function removeSearchFromHistory(id: string): boolean {
  const index = searchHistory.findIndex((item) => item.id === id);
  if (index === -1) return false;
  searchHistory.splice(index, 1);
  return true;
}

/**
 * Get recent searches (limited).
 */
export function getRecentSearches(limit: number = 5): SearchHistoryItem[] {
  return searchHistory.slice(0, limit);
}

/**
 * Get popular searches by category.
 */
export function getPopularSearchesByCategory(
  category: PopularSearchItem["category"]
): PopularSearchItem[] {
  return popularSearches.filter((item) => item.category === category);
}

/**
 * Get trending searches (most popular with up trend).
 */
export function getTrendingSearches(limit: number = 3): PopularSearchItem[] {
  return popularSearches
    .filter((item) => item.trend === "up")
    .sort((a, b) => b.searchCount - a.searchCount)
    .slice(0, limit);
}

/**
 * Get search statistics.
 */
export function getSearchStats() {
  const totalSearches = searchHistory.length;
  const uniqueQueries = new Set(searchHistory.map((item) => item.query)).size;
  const mostSearched = searchHistory.reduce((acc, item) => {
    acc[item.query] = (acc[item.query] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const sorted = Object.entries(mostSearched).sort((a, b) => b[1] - a[1]);
  const topQueries = sorted.slice(0, 3).map(([query, count]) => ({ query, count }));

  return {
    totalSearches,
    uniqueQueries,
    topQueries,
    popularSearches: popularSearches.slice(0, 3),
  };
}

/**
 * Format search time for display.
 */
export function formatSearchTime(ms: number): string {
  if (ms < 1000) {
    return `${ms}ms`;
  }
  return `${(ms / 1000).toFixed(1)}s`;
}

/**
 * Get search result count message.
 */
export function getResultCountMessage(totalResults: number): string {
  if (totalResults === 0) return "No results found";
  if (totalResults === 1) return "1 result found";
  return `${totalResults} results found`;
}

/**
 * Check if search has results.
 */
export function hasSearchResults(response: SearchResponse): boolean {
  return response.totalResults > 0 && response.results.length > 0;
}

/**
 * Get pagination range display.
 */
export function getPaginationDisplay(response: SearchResponse): string {
  const { page = 1, limit = 20, totalResults = 0 } = response;
  if (totalResults === 0) return "No results";
  const start = (page - 1) * limit + 1;
  const end = Math.min(page * limit, totalResults);
  return `${start} - ${end} of ${totalResults}`;
}