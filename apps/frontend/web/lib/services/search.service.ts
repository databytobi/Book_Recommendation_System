/**
 * ================================================================
 * 🔍 Search Service
 * ================================================================
 *
 * Handles all search-related operations including:
 * - Searching books
 * - Getting search history
 * - Getting popular searches
 * - Managing search history (add, remove, clear)
 * - Getting search statistics
 *
 * Currently backed by mock data.
 * Will later communicate with the backend API.
 * ================================================================
 */

const API_BASE = "http://127.0.0.1:8000/api/v1";

// Import types from the types file
import type { 
  SearchHistoryItem, 
  PopularSearchItem, 
  SearchFilters, 
  SearchResponse,
  SearchResult
} from "@/lib/types/search";

// Keep only the service-specific types
export interface SearchSuggestion {
  text: string;
  type: 'book' | 'author' | 'genre';
}

class SearchService {
  /**
   * Search for books by query with optional filters
   */
  async searchBooks(query: string, filters?: SearchFilters, page: number = 1, limit: number = 20): Promise<SearchResponse> {
    if (query.trim().length < 2) {
      return {
        query,
        totalResults: 0,
        results: [],
        filters,
        page,
        limit,
        totalPages: 0,
        searchTimeMs: 0,
      };
    }

    try {
      // Build query parameters
      const params = new URLSearchParams();
      params.append('q', query);
      params.append('page', String(page));
      params.append('limit', String(limit));
      
      // Add filters if they exist
      if (filters) {
        if (filters.genre) params.append('genre', filters.genre);
        if (filters.language) params.append('language', filters.language);
        if (filters.minimumRating) params.append('minRating', String(filters.minimumRating));
        if (filters.publicationYear) params.append('year', String(filters.publicationYear));
        if (filters.author) params.append('author', filters.author);
        if (filters.publisher) params.append('publisher', filters.publisher);
        if (filters.startYear) params.append('startYear', String(filters.startYear));
        if (filters.endYear) params.append('endYear', String(filters.endYear));
        if (filters.format) params.append('format', filters.format);
        if (filters.availableOnly) params.append('availableOnly', 'true');
      }

      const startTime = Date.now();
      const response = await fetch(
        `${API_BASE}/books/search?${params.toString()}`,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to search books");
      }

      const data = await response.json();
      const searchTimeMs = Date.now() - startTime;

      // Transform the response into the canonical UI Book shape declared by
      // SearchResultBook (lib/types/book.ts): author is an object, the cover
      // lives in `cover`, the rating in `rating`. The previous mapping used
      // `imageUrl`/`averageRating`/`author` (a bare string) — fields nothing
      // renders — so every result showed "no cover available" and
      // "Unknown Author".
      const results: SearchResult[] = (data.results || []).map((book: any) => {
        const authorName: string = Array.isArray(book.authors)
          ? book.authors.join(", ")
          : book.authors || "Unknown Author";

        return {
          book: {
            id: book.isbn || book.id || `book_${Date.now()}`,
            isbn: book.isbn || "",
            title: book.title || "",
            author: {
              id: authorName,
              name: authorName,
            },
            authors: Array.isArray(book.authors)
              ? book.authors
              : [book.authors].filter(Boolean),
            cover: book.image_url || book.imageUrl || undefined,
            publicationYear: book.publication_year || book.publicationYear || undefined,
            rating: book.average_rating || book.averageRating || undefined,
            averageRating: book.average_rating || book.averageRating || 0,
            ratingsCount: book.ratings_count || book.ratingsCount || 0,
            genres: book.genre ? [book.genre] : [],
            genre: book.genre || undefined,
            publisher: book.publisher || "",
            description: book.description || "",
            relevanceScore: 0.5,
            matchedText: book.title || "",
          },
          similarityScore: 0.5,
          highlights: [],
        };
      });

      return {
        query,
        totalResults: data.total || data.results?.length || 0,
        results,
        filters,
        searchTimeMs,
        page,
        limit,
        totalPages: Math.ceil((data.total || 0) / limit),
        suggestions: [],
      };
    } catch (error) {
      console.error('Error searching books:', error);
      throw new Error('Failed to search books');
    }
  }

  /**
   * Get search history from localStorage
   */
  async getSearchHistory(): Promise<SearchHistoryItem[]> {
    if (typeof window === 'undefined') return [];

    try {
      const history = localStorage.getItem('searchHistory');
      if (history) {
        const parsed = JSON.parse(history);
        if (Array.isArray(parsed)) {
          return parsed;
        }
      }
    } catch (_err) {
      console.warn('Failed to load search history:', _err);
    }
    return [];
  }

  /**
   * Save a search term to history
   */
  async saveSearchTerm(term: string, resultCount?: number): Promise<void> {
    if (!term || term.trim().length === 0 || typeof window === 'undefined') return;

    try {
      const history = await this.getSearchHistory();
      
      const now = new Date();
      const newItem: SearchHistoryItem = {
        id: `search_${Date.now()}`,
        query: term,
        searchedAt: now.toISOString(),
        searchedAtDisplay: this.getTimeAgo(now),
        resultCount: resultCount || 0,
      };
      
      // Remove duplicate queries (keep the newest)
      const filtered = history.filter(item => item.query !== term);
      
      // Add new item at the beginning, keep last 10
      const updated = [newItem, ...filtered].slice(0, 10);
      
      localStorage.setItem('searchHistory', JSON.stringify(updated));
    } catch (_err) {
      console.warn('Failed to save search term:', _err);
    }
  }

  /**
   * Clear search history
   */
  async clearSearchHistory(): Promise<void> {
    if (typeof window === 'undefined') return;

    try {
      localStorage.removeItem('searchHistory');
    } catch (_err) {
      console.warn('Failed to clear search history:', _err);
    }
  }

  /**
   * Remove a specific search term from history by ID
   */
  async removeSearchTerm(id: string): Promise<void> {
    if (!id || typeof window === 'undefined') return;

    try {
      const history = await this.getSearchHistory();
      const updated = history.filter(item => item.id !== id);
      localStorage.setItem('searchHistory', JSON.stringify(updated));
    } catch (_err) {
      console.warn('Failed to remove search term:', _err);
    }
  }

  /**
   * Get popular searches
   */
  async getPopularSearches(limit: number = 5): Promise<PopularSearchItem[]> {
    try {
      // In production, this would be an API call:
      // const response = await fetch(`${API_BASE}/search/popular?limit=${limit}`);
      // return response.json();

      // Return mock data as PopularSearchItem[] with 'as const' for trend
      return [
        { query: 'The Great Gatsby', searchCount: 1250, trend: 'up' as const, changePercentage: 15, category: 'book' as const },
        { query: '1984', searchCount: 980, trend: 'neutral' as const, changePercentage: 0, category: 'book' as const },
        { query: 'To Kill a Mockingbird', searchCount: 870, trend: 'up' as const, changePercentage: 8, category: 'book' as const },
        { query: 'Pride and Prejudice', searchCount: 750, trend: 'down' as const, changePercentage: -5, category: 'book' as const },
        { query: 'The Catcher in the Rye', searchCount: 620, trend: 'up' as const, changePercentage: 3, category: 'book' as const },
      ].slice(0, limit);
    } catch (error) {
      console.error('Error getting popular searches:', error);
      return [];
    }
  }

  /**
   * Get trending searches
   */
  async getTrendingSearches(limit: number = 5): Promise<PopularSearchItem[]> {
    try {
      // In production, this would be an API call:
      // const response = await fetch(`${API_BASE}/search/trending?limit=${limit}`);
      // return response.json();

      // Return mock data as PopularSearchItem[] with 'as const' for trend
      return [
        { query: 'Dune', searchCount: 450, trend: 'up' as const, changePercentage: 45, category: 'book' as const },
        { query: 'Harry Potter', searchCount: 380, trend: 'up' as const, changePercentage: 22, category: 'book' as const },
        { query: 'The Hobbit', searchCount: 320, trend: 'neutral' as const, changePercentage: 2, category: 'book' as const },
        { query: 'Foundation', searchCount: 280, trend: 'up' as const, changePercentage: 18, category: 'book' as const },
        { query: 'The Alchemist', searchCount: 250, trend: 'down' as const, changePercentage: -8, category: 'book' as const },
      ].slice(0, limit);
    } catch (error) {
      console.error('Error getting trending searches:', error);
      return [];
    }
  }

  /**
   * Get search suggestions based on partial query
   */
  async getSuggestions(query: string): Promise<SearchSuggestion[]> {
    if (!query || query.trim().length < 2) {
      return [];
    }

    try {
      // In production, this would be an API call:
      // const response = await fetch(
      //   `${API_BASE}/search/suggestions?q=${encodeURIComponent(query)}`
      // );
      // return response.json();

      return [];
    } catch (error) {
      console.error('Error getting suggestions:', error);
      return [];
    }
  }

  /**
   * Get search statistics
   */
  async getSearchStats(): Promise<{
    totalSearches: number;
    popularQueries: { query: string; count: number }[];
    averageResultsPerSearch: number;
  }> {
    try {
      // In production, this would be an API call:
      // const response = await fetch(`${API_BASE}/search/stats`);
      // return response.json();

      return {
        totalSearches: 0,
        popularQueries: [],
        averageResultsPerSearch: 0,
      };
    } catch (error) {
      console.error('Error getting search stats:', error);
      return {
        totalSearches: 0,
        popularQueries: [],
        averageResultsPerSearch: 0,
      };
    }
  }

  /**
   * Helper: Get a human-readable time ago string
   */
  private getTimeAgo(date: Date): string {
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
      const weeks = Math.floor(diffDays / 7);
      return `${weeks} week${weeks > 1 ? "s" : ""} ago`;
    } else {
      return date.toLocaleDateString();
    }
  }
}

// ============================================================
// 📦 Export Singleton Instance
// ============================================================

export const searchService = new SearchService();
//export type { SearchSuggestion };