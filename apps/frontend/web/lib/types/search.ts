/**
 * ================================================================
 * 🔍 Search Types
 * ================================================================
 *
 * These types define the search system's data structures.
 * They handle:
 * - Search history
 * - Popular searches
 * - Search filters
 * - Search results and responses
 * ================================================================
 */

import type { ISODateString } from "./common";
import type { SearchResultBook } from "./book";

// ============================================================
// 📜 Search History
// ============================================================

/**
 * Search history entry.
 *
 * Represents a single search query performed by the user.
 * Used in the search history page and autocomplete suggestions.
 */
export interface SearchHistoryItem {
  /** Unique identifier for the history entry (always a string) */
  id: string; // ✅ Changed from ID to string

  /** The search query string */
  query: string;

  /** ISO timestamp of when the search was performed */
  searchedAt: ISODateString;

  /** Display-friendly time (e.g., "2 hours ago", "Today") */
  searchedAtDisplay?: string;

  /** Number of results returned for this search */
  resultCount?: number;
}

// ============================================================
// 🔥 Popular Searches
// ============================================================

/**
 * Popular searches displayed to users.
 *
 * Shows trending or frequently searched queries
 * to help users discover content.
 */
export interface PopularSearchItem {
  /** The search query string */
  query: string;

  /** Number of times this search has been performed */
  searchCount: number;

  /** Trend direction: up, down, or neutral */
  trend?: "up" | "down" | "neutral";

  /** Percentage change compared to previous period */
  changePercentage?: number;

  /** Category of the search (e.g., "book", "author", "genre") */
  category?: "book" | "author" | "genre" | "all";
}

// ============================================================
// 🔧 Search Filters
// ============================================================

/**
 * Search filters selected by the user.
 *
 * Used to refine search results and narrow down
 * the list of matching books.
 */
export interface SearchFilters {
  /** Filter by genre (e.g., "Science Fiction", "Fantasy") */
  genre?: string;

  /** Filter by language (e.g., "English", "Spanish") */
  language?: string;

  /** Filter by minimum rating (1-5) */
  minimumRating?: number;

  /** Filter by publication year */
  publicationYear?: number;

  /** Filter by author name */
  author?: string;

  /** Filter by publisher */
  publisher?: string;

  /** Filter by date range - start year */
  startYear?: number;

  /** Filter by date range - end year */
  endYear?: number;

  /** Filter by book format (e.g., "Paperback", "eBook") */
  format?: "paperback" | "hardcover" | "ebook" | "audiobook";

  /** Whether to show only available books */
  availableOnly?: boolean;
}

// ============================================================
// 📚 Search Result
// ============================================================

/**
 * Represents a single matched book.
 *
 * Extends the base book with a similarity score
 * indicating how well it matches the search query.
 */
export interface SearchResult {
  /** The matched book with search-specific metadata */
  book: SearchResultBook;

  /** Similarity score (0-1) indicating how well the book matches the query */
  similarityScore?: number;

  /** Highlighted text snippets showing the match */
  highlights?: string[];
}

// ============================================================
// 📊 Search Response
// ============================================================

/**
 * Complete response returned by the search engine.
 *
 * Contains the search results along with metadata
 * about the search query and applied filters.
 */
export interface SearchResponse {
  /** The original search query */
  query: string;

  /** Total number of results found */
  totalResults: number;

  /** List of matching search results */
  results: SearchResult[];

  /** Applied search filters (if any) */
  filters?: SearchFilters;

  /** Time taken to perform the search (in milliseconds) */
  searchTimeMs?: number;

  /** Suggested alternative queries (for "Did you mean?") */
  suggestions?: string[];

  /** Pagination information */
  page?: number;
  limit?: number;
  totalPages?: number;
}

// ============================================================
// 🏗️ Factory Functions
// ============================================================

/**
 * Create a search history item.
 */
export function createSearchHistoryItem(params: {
  id?: string; // ✅ Changed from ID to string
  query: string;
  searchedAt?: ISODateString;
  resultCount?: number;
}): SearchHistoryItem {
  return {
    id: params.id || `search_${Date.now()}`,
    query: params.query,
    searchedAt: params.searchedAt || new Date().toISOString(),
    searchedAtDisplay: getTimeAgo(params.searchedAt || new Date().toISOString()),
    resultCount: params.resultCount,
  };
}

/**
 * Create a popular search item.
 */
export function createPopularSearchItem(params: {
  query: string;
  searchCount: number;
  trend?: "up" | "down" | "neutral";
  changePercentage?: number;
  category?: "book" | "author" | "genre" | "all";
}): PopularSearchItem {
  return {
    query: params.query,
    searchCount: params.searchCount,
    trend: params.trend || "neutral",
    changePercentage: params.changePercentage,
    category: params.category || "all",
  };
}

/**
 * Create a search result.
 */
export function createSearchResult(params: {
  book: SearchResultBook;
  similarityScore?: number;
  highlights?: string[];
}): SearchResult {
  return {
    book: params.book,
    similarityScore: params.similarityScore,
    highlights: params.highlights,
  };
}

/**
 * Create an empty search response.
 * 
 * @param query - The search query string
 * @param limit - Results per page (default: 20)
 * @returns An empty search response with default pagination
 */
export function createEmptySearchResponse(
  query: string,
  limit: number = 20
): SearchResponse {
  return {
    query,
    totalResults: 0,
    results: [],
    searchTimeMs: 0,
    page: 1,
    limit,
    totalPages: 0,
  };
}

// ============================================================
// 🔄 Helper Functions
// ============================================================

/**
 * Get a human-readable time ago string.
 */
function getTimeAgo(dateString: ISODateString): string {
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    const diffDays = diffTime / (1000 * 60 * 60 * 24);
    
    if (diffDays < 1) {
      return "Today";
    } else if (diffDays < 2) {
      return "Yesterday";
    } else if (diffDays < 7) {
      return `${Math.floor(diffDays)} days ago`;
    } else if (diffDays < 30) {
      return `${Math.floor(diffDays / 7)} week${Math.floor(diffDays / 7) > 1 ? "s" : ""} ago`;
    } else {
      return date.toLocaleDateString();
    }
  } catch {
    return dateString;
  }
}

/**
 * Format a search time for display.
 * 
 * @param ms - Time in milliseconds
 * @returns Formatted time string (e.g., "245ms" or "2.3s")
 */
export function formatSearchTime(ms: number): string {
  const timeMs = typeof ms === 'number' ? ms : Number(ms) || 0;
  if (timeMs < 1000) {
    return `${timeMs}ms`;
  }
  return `${(timeMs / 1000).toFixed(1)}s`;
}

/**
 * Get the display label for a search category.
 */
export function getCategoryLabel(
  category: PopularSearchItem["category"]
): string {
  const labels = {
    book: "Books",
    author: "Authors",
    genre: "Genres",
    all: "All",
  };
  return labels[category || "all"] || "All";
}

/**
 * Check if there are any filters applied.
 */
export function hasFilters(filters?: SearchFilters): boolean {
  if (!filters) return false;
  return !!(
    filters.genre ||
    filters.language ||
    filters.minimumRating ||
    filters.publicationYear ||
    filters.author ||
    filters.publisher ||
    filters.startYear ||
    filters.endYear ||
    filters.format ||
    filters.availableOnly
  );
}

/**
 * Get the number of active filters.
 */
export function getActiveFilterCount(filters?: SearchFilters): number {
  if (!filters) return 0;
  let count = 0;
  if (filters.genre) count++;
  if (filters.language) count++;
  if (filters.minimumRating) count++;
  if (filters.publicationYear) count++;
  if (filters.author) count++;
  if (filters.publisher) count++;
  if (filters.startYear) count++;
  if (filters.endYear) count++;
  if (filters.format) count++;
  if (filters.availableOnly) count++;
  return count;
}

/**
 * Get the display label for a filter value.
 */
export function getFilterDisplayLabel(filters: SearchFilters): string[] {
  const labels: string[] = [];
  
  if (filters.genre) labels.push(`Genre: ${filters.genre}`);
  if (filters.language) labels.push(`Language: ${filters.language}`);
  if (filters.minimumRating) labels.push(`⭐ ${filters.minimumRating}+`);
  if (filters.publicationYear) labels.push(`Year: ${filters.publicationYear}`);
  if (filters.author) labels.push(`Author: ${filters.author}`);
  if (filters.publisher) labels.push(`Publisher: ${filters.publisher}`);
  if (filters.startYear && filters.endYear) {
    labels.push(`${filters.startYear} - ${filters.endYear}`);
  }
  if (filters.format) labels.push(`Format: ${filters.format}`);
  if (filters.availableOnly) labels.push("Available only");
  
  return labels;
}

/**
 * Check if search has results.
 */
export function hasResults(response: SearchResponse): boolean {
  return response.totalResults > 0 && response.results.length > 0;
}

/**
 * Get the number of results per page.
 */
export function getResultsPerPage(response: SearchResponse): number {
  return response.limit || 20;
}

/**
 * Get the current page number.
 */
export function getCurrentPage(response: SearchResponse): number {
  return response.page || 1;
}

/**
 * Get the total number of pages.
 */
export function getTotalPages(response: SearchResponse): number {
  return response.totalPages || 0;
}

/**
 * Get the pagination range for display.
 */
export function getPaginationRange(response: SearchResponse): string {
  const page = getCurrentPage(response);
  const limit = getResultsPerPage(response);
  const total = response.totalResults;
  
  if (total === 0) return "No results";
  
  const start = (page - 1) * limit + 1;
  const end = Math.min(page * limit, total);
  
  return `${start} - ${end} of ${total}`;
}

/**
 * Get the similarity score as a percentage.
 */
export function getSimilarityPercentage(result: SearchResult): string {
  if (!result.similarityScore) return "N/A";
  const score = typeof result.similarityScore === 'number' 
    ? result.similarityScore 
    : Number(result.similarityScore) || 0;
  return `${Math.round(score * 100)}%`;
}

/**
 * Check if a result has a high similarity score (> 0.8).
 */
export function isHighMatch(result: SearchResult): boolean {
  const score = typeof result.similarityScore === 'number'
    ? result.similarityScore
    : Number(result.similarityScore) || 0;
  return score > 0.8;
}

/**
 * Check if a result has a medium similarity score (0.5 - 0.8).
 */
export function isMediumMatch(result: SearchResult): boolean {
  const score = typeof result.similarityScore === 'number'
    ? result.similarityScore
    : Number(result.similarityScore) || 0;
  return score > 0.5 && score <= 0.8;
}

/**
 * Check if a result has a low similarity score (< 0.5).
 */
export function isLowMatch(result: SearchResult): boolean {
  const score = typeof result.similarityScore === 'number'
    ? result.similarityScore
    : Number(result.similarityScore) || 0;
  return score <= 0.5;
}

/**
 * Get the top N results by similarity score.
 */
export function getTopResults(
  results: SearchResult[],
  limit: number = 10
): SearchResult[] {
  return [...results]
    .sort((a: SearchResult, b: SearchResult) => {
      const scoreA = typeof a.similarityScore === 'number' ? a.similarityScore : Number(a.similarityScore) || 0;
      const scoreB = typeof b.similarityScore === 'number' ? b.similarityScore : Number(b.similarityScore) || 0;
      return scoreB - scoreA;
    })
    .slice(0, limit);
}

/**
 * Filter results by minimum similarity score.
 */
export function filterByMinScore(
  results: SearchResult[],
  minScore: number = 0.5
): SearchResult[] {
  return results.filter((result: SearchResult) => {
    const score = typeof result.similarityScore === 'number'
      ? result.similarityScore
      : Number(result.similarityScore) || 0;
    return score >= minScore;
  });
}

/**
 * Get the average similarity score of results.
 */
export function getAverageScore(results: SearchResult[]): number {
  if (results.length === 0) return 0;
  const total = results.reduce((sum: number, result: SearchResult) => {
    const score = typeof result.similarityScore === 'number'
      ? result.similarityScore
      : Number(result.similarityScore) || 0;
    return sum + score;
  }, 0);
  return Math.round((total / results.length) * 100) / 100;
}