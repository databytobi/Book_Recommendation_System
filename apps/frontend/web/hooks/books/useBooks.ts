/**
 * ================================================================
 * 📚 useBooks Hook
 * ================================================================
 *
 * A custom React hook for fetching and managing books.
 * 
 * Features:
 * - Fetches all books on mount
 * - Handles loading and error states
 * - Provides search functionality
 * - Offers book filtering and sorting
 * - Caches results to prevent unnecessary requests
 * 
 * @example
 * ```tsx
 * const { books, loading, searchBooks, filterByGenre } = useBooks();
 * 
 * if (loading) return <LoadingSpinner />;
 * if (error) return <ErrorMessage error={error} />;
 * 
 * return (
 *   <div>
 *     <SearchBar onSearch={searchBooks} />
 *     <FilterBar onFilter={filterByGenre} />
 *     {books.map(book => (
 *       <BookCard key={book.isbn} book={book} />
 *     ))}
 *   </div>
 * );
 * ```
 * ================================================================
 */

import { useEffect, useState, useCallback, useRef, useMemo } from "react";

import { bookService, type Book } from "@/lib/services";

// ============================================================
// 📋 Types
// ============================================================

interface UseBooksOptions {
  /** Automatically fetch on mount (default: true) */
  autoFetch?: boolean;
  
  /** Enable caching (default: true) */
  cache?: boolean;
  
  /** Cache key (default: 'books-cache') */
  cacheKey?: string;
  
  /** Initial search query */
  initialQuery?: string;
  
  /** Initial genre filter */
  initialGenre?: string;
}

interface UseBooksReturn {
  /** List of books */
  books: Book[];
  
  /** Filtered list of books */
  filteredBooks: Book[];
  
  /** Whether data is currently loading */
  loading: boolean;
  
  /** Error object if request failed */
  error: Error | null;
  
  /** Current search query */
  searchQuery: string;
  
  /** Current genre filter */
  genreFilter: string | null;
  
  /** Search for books */
  searchBooks: (query: string) => Promise<void>;
  
  /** Filter books by genre */
  filterByGenre: (genre: string | null) => void;
  
  /** Clear all filters */
  clearFilters: () => void;
  
  /** Get a book by ID - async version */
  getBookById: (id: number) => Promise<Book | undefined>;
  
  /** Get top rated books */
  getTopRatedBooks: (limit?: number) => Book[];
  
  /** Get recent books */
  getRecentBooks: (limit?: number) => Book[];
  
  /** Get random books */
  getRandomBooks: (count?: number) => Book[];
  
  /** Manually refetch books */
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
 * Custom hook for fetching and managing books.
 * 
 * @param options - Configuration options
 * @returns {UseBooksReturn} - Books data and utilities
 * 
 * @example
 * ```tsx
 * // Basic usage
 * const { books, loading, searchBooks } = useBooks();
 * 
 * // With options
 * const { books, loading, refetch, filterByGenre } = useBooks({
 *   autoFetch: true,
 *   cache: true,
 * });
 * 
 * // Search for books
 * const handleSearch = async (query: string) => {
 *   await searchBooks(query);
 * };
 * ```
 */
export function useBooks(options: UseBooksOptions = {}): UseBooksReturn {
  const {
    autoFetch = true,
    cache = true,
    cacheKey = 'books-cache',
    initialQuery = "",
    initialGenre = null,
  } = options;

  // ============================================================
  // 📦 State
  // ============================================================

  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>(initialQuery);
  const [genreFilter, setGenreFilter] = useState<string | null>(initialGenre);
  const isMounted = useRef<boolean>(true);

  // ============================================================
  // 📊 Derived State
  // ============================================================

  /**
   * Filter books based on search query and genre filter.
   */
  const filteredBooks = useMemo((): Book[] => {
    let result = [...books];

    // Apply search filter
    if (searchQuery && searchQuery.trim().length > 0) {
      const query = searchQuery.toLowerCase().trim();
      result = result.filter(
        (book) =>
          book.title.toLowerCase().includes(query) ||
          book.authors.some(author => author.toLowerCase().includes(query))
      );
    }

    // Apply genre filter
    if (genreFilter && genreFilter.trim().length > 0) {
      const genre = genreFilter.toLowerCase().trim();
      result = result.filter(
        (book) =>
          book.title.toLowerCase().includes(genre) ||
          book.authors.some(author => author.toLowerCase().includes(genre)) ||
          (book.genre && book.genre.toLowerCase().includes(genre))
      );
    }

    return result;
  }, [books, searchQuery, genreFilter]);

  // ============================================================
  // 🛠️ Helper Functions
  // ============================================================

  /**
   * Load cached data from localStorage.
   */
  const loadFromCache = useCallback((): Book[] | null => {
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
      console.warn('Failed to load books from cache:', _err);
    }
    return null;
  }, [cache, cacheKey]);

  /**
   * Save data to cache.
   */
  const saveToCache = useCallback((data: Book[]) => {
    if (!cache || typeof window === 'undefined') return;
    
    try {
      localStorage.setItem(cacheKey, JSON.stringify(data));
    } catch (_err) {
      console.warn('Failed to save books to cache:', _err);
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
   * Fetch all books.
   */
  const fetchBooks = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      const data = await bookService.getBooks();
      
      if (isMounted.current) {
        // Extract the books array from the response
        const booksData = data.books;
        setBooks(booksData);
        saveToCache(booksData);
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
   * Search for books using the book service.
   */
  const searchBooks = useCallback(async (query: string): Promise<void> => {
    setSearchQuery(query);
    
    if (!query || query.trim().length === 0) {
      // If query is empty, fetch all books
      await fetchBooks();
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const results = await bookService.searchBooks(query);
      
      if (isMounted.current) {
        setBooks(results);
      }
    } catch (err) {
      if (isMounted.current) {
        const error = err as Error;
        setError(error);
      }
    } finally {
      if (isMounted.current) {
        setLoading(false);
      }
    }
  }, [fetchBooks]);

  /**
   * Filter books by genre.
   */
  const filterByGenre = useCallback((genre: string | null): void => {
    setGenreFilter(genre);
  }, []);

  /**
   * Clear all filters.
   */
  const clearFilters = useCallback((): void => {
    setSearchQuery(initialQuery);
    setGenreFilter(null);
    void fetchBooks();
  }, [initialQuery, fetchBooks]);

  /**
   * Get a book by ID using the book service.
   */
  const getBookById = useCallback(async (id: number): Promise<Book | undefined> => {
    // First check local state - convert id to string since isbn is a string
    const localBook = books.find(book => book.isbn === id.toString());
    if (localBook) return localBook;
    
    // If not found locally, try the service
    try {
      return await bookService.getBookById(id);
    } catch {
      return undefined;
    }
  }, [books]);

  /**
   * Get top rated books from the current list.
   */
  const getTopRatedBooks = useCallback((limit: number = 5): Book[] => {
    return [...books]
      .sort((a, b) => (b.average_rating || 0) - (a.average_rating || 0))
      .slice(0, limit);
  }, [books]);

  /**
   * Get recent books from the current list.
   */
  const getRecentBooks = useCallback((limit: number = 5): Book[] => {
    return [...books]
      .sort((a, b) => (b.publication_year || 0) - (a.publication_year || 0))
      .slice(0, limit);
  }, [books]);

  /**
   * Get random books from the current list.
   */
  const getRandomBooks = useCallback((count: number = 3): Book[] => {
    if (count <= 0 || books.length === 0) return [];
    
    const shuffled = [...books];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled.slice(0, Math.min(count, shuffled.length));
  }, [books]);

  /**
   * Reset the hook state.
   */
  const reset = useCallback(() => {
    setBooks([]);
    setLoading(true);
    setError(null);
    setSearchQuery(initialQuery);
    setGenreFilter(initialGenre);
    clearCache();
    void fetchBooks();
  }, [clearCache, fetchBooks, initialQuery, initialGenre]);

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

    return () => {
      isMounted.current = false;
    };
  }, [autoFetch, cache, fetchBooks, loadFromCache]);

  // ============================================================
  // 📦 Return
  // ============================================================

  return {
    books,
    filteredBooks,
    loading,
    error,
    searchQuery,
    genreFilter,
    searchBooks,
    filterByGenre,
    clearFilters,
    getBookById,
    getTopRatedBooks,
    getRecentBooks,
    getRandomBooks,
    refetch,
    clearCache,
    reset,
  };
}

// ============================================================
// 🔄 Sub-hooks
// ============================================================

/**
 * useBook - Hook for getting a single book by ID.
 * 
 * @param bookId - The book ID
 * @returns Book data and loading state
 * 
 * @example
 * ```tsx
 * const { book, loading } = useBook(1);
 * 
 * return (
 *   <div>
 *     {loading ? <LoadingSpinner /> : <BookDetails book={book} />}
 *   </div>
 * );
 * ```
 */
export function useBook(bookId: number) {
  const [book, setBook] = useState<Book | undefined>(undefined);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const { getBookById } = useBooks({ autoFetch: true });

  useEffect(() => {
    let isMounted = true;
    const fetchBook = async () => {
      setLoading(true);
      try {
        const result = await getBookById(bookId);
        if (isMounted) {
          setBook(result);
        }
      } catch (err) {
        if (isMounted) {
          setError(err as Error);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };
    fetchBook();
    return () => {
      isMounted = false;
    };
  }, [bookId, getBookById]);

  return {
    book,
    loading,
    error,
  };
}

/**
 * useTopBooks - Hook for getting top rated books.
 * 
 * @param limit - Number of books to return (default: 5)
 * @returns Top rated books
 * 
 * @example
 * ```tsx
 * const { books, loading } = useTopBooks(5);
 * 
 * return (
 *   <div>
 *     {books.map(book => (
 *       <BookCard key={book.isbn} book={book} />
 *     ))}
 *   </div>
 * );
 * ```
 */
export function useTopBooks(limit: number = 5) {
  const { getTopRatedBooks, loading } = useBooks({ autoFetch: true });
  
  const books = getTopRatedBooks(limit);
  
  return {
    books,
    loading,
  };
}

/**
 * useRecentBooks - Hook for getting recent books.
 * 
 * @param limit - Number of books to return (default: 5)
 * @returns Recent books
 * 
 * @example
 * ```tsx
 * const { books, loading } = useRecentBooks(3);
 * 
 * return (
 *   <div>
 *     {books.map(book => (
 *       <BookCard key={book.isbn} book={book} />
 *     ))}
 *   </div>
 * );
 * ```
 */
export function useRecentBooks(limit: number = 5) {
  const { getRecentBooks, loading } = useBooks({ autoFetch: true });
  
  const books = getRecentBooks(limit);
  
  return {
    books,
    loading,
  };
}

/**
 * useBookSearch - Hook for searching books.
 * 
 * @returns Search functions and results
 * 
 * @example
 * ```tsx
 * const { results, search, loading } = useBookSearch();
 * 
 * const handleSearch = (query: string) => {
 *   search(query);
 * };
 * ```
 */
export function useBookSearch() {
  const { filteredBooks, searchBooks, loading, error } = useBooks({ autoFetch: true });
  
  return {
    results: filteredBooks,
    search: searchBooks,
    loading,
    error,
  };
}

// ============================================================
// 📦 Export Default
// ============================================================

export default useBooks;