/**
 * ================================================================
 * 📚 Book Service
 * ================================================================
 *
 * Handles all book-related operations including:
 * - Fetching books
 * - Getting book by ID
 * - Searching books
 * - Filtering books
 *
 * Currently backed by mock data.
 * Will later communicate with the backend API.
 * ================================================================
 */

const API_BASE = "http://127.0.0.1:8000/api/v1";

export interface Book {
  isbn: string;
  title: string;
  authors: string[];
  genre?: string | null;
  publisher?: string | null;
  publication_year?: number | null;
  image_url?: string | null;
  average_rating?: number | null;
  ratings_count?: number | null;
}

export interface BookListResponse {
  books: Book[];
  total: number;
  page: number;
  limit: number;
}

// ============================================================
// 📚 Book Service Class
// ============================================================

class BookService {
  /**
   * Returns paginated list of books.
   * 
   * @param page - Page number (default: 1)
   * @param limit - Number of books per page (default: 20)
   * @returns Promise<BookListResponse> - Paginated books response
   * 
   * @example
   * ```ts
   * const response = await bookService.getBooks(1, 20);
   * console.log(response.books); // Array of books
   * console.log(response.total); // Total number of books
   * ```
   */
  async getBooks(
    page = 1,
    limit = 20
  ): Promise<BookListResponse> {
    const response = await fetch(
      `${API_BASE}/books?page=${page}&limit=${limit}`
    );

    if (!response.ok) {
      throw new Error("Failed to fetch books");
    }

    return response.json();
  }

  /**
   * Returns a single book by ID.
   * 
   * @param id - The book ID to look up
   * @returns Promise<Book | undefined> - The book if found, undefined otherwise
   * 
   * @example
   * ```ts
   * const book = await bookService.getBookById(1);
   * if (book) {
   *   console.log(book.title);
   * }
   * ```
   */
  async getBookById(id: number): Promise<Book | undefined> {
    if (!id || id <= 0) {
      throw new Error("Invalid book ID");
    }

    try {
      // In production, this would be an API call:
      // const response = await fetch(`/api/books/${id}`);
      // return response.json();
      // TODO: Replace with actual API call
      throw new Error("Not implemented");
    } catch (error) {
      console.error(`Error fetching book with ID ${id}:`, error);
      throw new Error(`Failed to fetch book with ID ${id}`);
    }
  }

  /**
   * Search for books by query string.
   * 
   * @param query - The search query
   * @returns Promise<Book[]> - Array of matching books
   * 
   * @example
   * ```ts
   * const results = await bookService.searchBooks("Atomic");
   * console.log(results); // Books matching "Atomic"
   * ```
   */
  async searchBooks(query: string): Promise<Book[]> {
    if (!query || query.trim().length === 0) {
      return [];
    }

    try {
      // In production, this would be an API call:
      // const response = await fetch(`/api/books/search?q=${encodeURIComponent(query)}`);
      // return response.json();
      
      // TODO: Replace with actual API call
      throw new Error("Not implemented");
    } catch (error) {
      console.error(`Error searching books with query "${query}":`, error);
      throw new Error(`Failed to search books with query "${query}"`);
    }
  }

  /**
   * Get books by author name.
   * 
   * @param authorName - The author name to search for
   * @returns Promise<Book[]> - Array of books by the author
   * 
   * @example
   * ```ts
   * const books = await bookService.getBooksByAuthor("James Clear");
   * console.log(books); // Books by James Clear
   * ```
   */
  async getBooksByAuthor(authorName: string): Promise<Book[]> {
    if (!authorName || authorName.trim().length === 0) {
      return [];
    }

    try {
      // TODO: Replace with actual API call
      throw new Error("Not implemented");
    } catch (error) {
      console.error(`Error fetching books by author "${authorName}":`, error);
      throw new Error(`Failed to fetch books by author "${authorName}"`);
    }
  }

  /**
   * Get books by genre.
   * 
   * @param genre - The genre to filter by
   * @returns Promise<Book[]> - Array of books in the genre
   * 
   * @example
   * ```ts
   * const books = await bookService.getBooksByGenre("Fantasy");
   * console.log(books); // Fantasy books
   * ```
   */
  async getBooksByGenre(genre: string): Promise<Book[]> {
    if (!genre || genre.trim().length === 0) {
      return [];
    }

    try {
      // In production, this would be an API call:
      // const response = await fetch(`/api/books/genre/${encodeURIComponent(genre)}`);
      // return response.json();
      
      // TODO: Replace with actual API call
      throw new Error("Not implemented");
    } catch (error) {
      console.error(`Error fetching books by genre "${genre}":`, error);
      throw new Error(`Failed to fetch books by genre "${genre}"`);
    }
  }

  /**
   * Get top rated books.
   * 
   * @param limit - Maximum number of books to return (default: 5)
   * @returns Promise<Book[]> - Array of top rated books
   * 
   * @example
   * ```ts
   * const topBooks = await bookService.getTopRatedBooks(3);
   * console.log(topBooks); // Top 3 rated books
   * ```
   */
  async getTopRatedBooks(limit: number = 5): Promise<Book[]> {
    if (limit <= 0) {
      return [];
    }

    try {
      // TODO: Replace with actual API call
      throw new Error("Not implemented");
    } catch (error) {
      console.error("Error fetching top rated books:", error);
      throw new Error("Failed to fetch top rated books");
    }
  }

  /**
   * Get recently published books.
   * 
   * @param limit - Maximum number of books to return (default: 5)
   * @returns Promise<Book[]> - Array of recent books
   * 
   * @example
   * ```ts
   * const recentBooks = await bookService.getRecentBooks(3);
   * console.log(recentBooks); // 3 most recent books
   * ```
   */
  async getRecentBooks(limit: number = 5): Promise<Book[]> {
    if (limit <= 0) {
      return [];
    }

    try {
      // TODO: Replace with actual API call
      throw new Error("Not implemented");
    } catch (error) {
      console.error("Error fetching recent books:", error);
      throw new Error("Failed to fetch recent books");
    }
  }

  /**
   * Get a random selection of books.
   * 
   * @param count - Number of books to return (default: 3)
   * @returns Promise<Book[]> - Array of random books
   * 
   * @example
   * ```ts
   * const randomBooks = await bookService.getRandomBooks(2);
   * console.log(randomBooks); // 2 random books
   * ```
   */
  async getRandomBooks(count: number = 3): Promise<Book[]> {
    if (count <= 0) {
      return [];
    }

    try {
      // TODO: Replace with actual API call
      throw new Error("Not implemented");
    } catch (error) {
      console.error("Error fetching random books:", error);
      throw new Error("Failed to fetch random books");
    }
  }

  /**
   * Get book statistics.
   * 
   * @returns Promise<Object> - Book statistics
   * 
   * @example
   * ```ts
   * const stats = await bookService.getBookStats();
   * console.log(stats.totalBooks); // Total number of books
   * ```
   */
  async getBookStats() {
    try {
      // TODO: Replace with actual API call
      throw new Error("Not implemented");
    } catch (error) {
      console.error("Error fetching book stats:", error);
      throw new Error("Failed to fetch book stats");
    }
  }

  /**
   * Check if a book exists.
   * 
   * @param id - The book ID to check
   * @returns Promise<boolean> - True if the book exists
   * 
   * @example
   * ```ts
   * const exists = await bookService.bookExists(1);
   * console.log(exists); // true or false
   * ```
   */
  async bookExists(id: number): Promise<boolean> {
    if (!id || id <= 0) {
      return false;
    }

    try {
      const book = await this.getBookById(id);
      return !!book;
    } catch (error) {
      console.error(`Error checking if book with ID ${id} exists:`, error);
      return false;
    }
  }
}

// ============================================================
// 📦 Export Singleton Instance
// ============================================================

export const bookService = new BookService();
//export type { Book, BookListResponse };