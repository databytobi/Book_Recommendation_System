/**
 * ================================================================
 * 💡 Recommendation Service
 * ================================================================
 *
 * Handles all recommendation-related operations including:
 * - Getting recommendation sections
 * - Getting specific recommendation sections by ID
 * - Filtering recommendations
 * - Getting recommendation statistics
 *
 * Currently backed by mock data.
 * Will later communicate with the backend API.
 * ================================================================
 */

import {
  getRecommendations,
  getRecommendationSection,
  getAllRecommendationBooks,
  getHighestScoredRecommendation,
  getRecommendationsByAlgorithm,
  getHighConfidenceRecommendations,
  getFeaturedSections,
  getRandomRecommendation,
  getAverageRecommendationScore,
  getRecommendationStats,
  getTopRecommendations,
  isBookRecommended,
  getAlgorithmLabel,
  getConfidenceLabel,
  getConfidenceColor,
  filterByMinScore,
  sortByScore,
} from "@/lib/mock";

import type {
  RecommendationSection,
  RecommendationBook,
  RecommendationAlgorithm,
  RecommendationConfidence,
  Author,
} from "@/lib/types";

// ============================================================
// 💡 Recommendation Service Class
// ============================================================

class RecommendationService {
  /**
   * Safely create a recommendation with validation.
   * This ensures we don't create recommendations for invalid books.
   * 
   * @param book - The book to create a recommendation for
   * @returns The recommendation book or null if invalid
   */
  safeCreateRecommendation(book: unknown): RecommendationBook | null {
    // Guard against invalid book IDs
    if (!book || typeof book !== 'object' || book === null) {
      console.warn('⚠️ Skipping recommendation creation - invalid book:', book);
      return null;
    }

    const bookObj = book as Record<string, unknown>;
    
    // Check for valid ID
    const id = bookObj.id as number | undefined;
    if (!id || id === 0) {
      console.warn('⚠️ Skipping recommendation creation - invalid book ID:', book);
      return null;
    }
    
    // Safely extract author with proper Author type
    let author: Author;
    const authorData = bookObj.author;
    
    if (authorData && typeof authorData === 'object' && authorData !== null) {
      const authorObj = authorData as Record<string, unknown>;
      author = {
        id: (authorObj.id as number) || 0,
        name: (authorObj.name as string) || 'Unknown Author',
      };
    } else if (typeof authorData === 'string') {
      author = {
        id: 0,
        name: authorData,
      };
    } else {
      author = {
        id: 0,
        name: 'Unknown Author',
      };
    }
    
    // Build the recommendation object
    const recommendation: RecommendationBook = {
      id: id,
      title: (bookObj.title as string) || 'Unknown Title',
      author: author,
      rating: (bookObj.rating as number) || 0,
      score: (bookObj.score as number) || 75,
      algorithm: (bookObj.algorithm as RecommendationAlgorithm) || 'collaborative',
      confidence: (bookObj.confidence as RecommendationConfidence) || 'medium',
      reason: (bookObj.reason as string) || 'Recommended for you',
    };

    // Override with existing values if they're valid
    if (bookObj.score !== undefined && typeof bookObj.score === 'number') {
      recommendation.score = bookObj.score;
    }
    if (bookObj.algorithm && typeof bookObj.algorithm === 'string') {
      recommendation.algorithm = bookObj.algorithm as RecommendationAlgorithm;
    }
    if (bookObj.confidence && typeof bookObj.confidence === 'string') {
      recommendation.confidence = bookObj.confidence as RecommendationConfidence;
    }
    if (bookObj.reason && typeof bookObj.reason === 'string') {
      recommendation.reason = bookObj.reason;
    }
    
    return recommendation;
  }

  /**
   * Get all recommendation sections.
   * 
   * @returns Promise<RecommendationSection[]> - Array of recommendation sections
   * 
   * @example
   * ```ts
   * const sections = await recommendationService.getRecommendations();
   * console.log(sections); // All recommendation sections
   * ```
   */
  async getRecommendations(): Promise<RecommendationSection[]> {
    try {
      // In production, this would be an API call:
      // const response = await fetch('/api/recommendations');
      // return response.json();
      const sections = getRecommendations();
      
      // Filter out invalid books from each section
      return sections
        .map(section => ({
          ...section,
          books: section.books
            .map(book => this.safeCreateRecommendation(book))
            .filter((book): book is RecommendationBook => book !== null),
        }))
        .filter(section => section.books.length > 0);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
      throw new Error("Failed to fetch recommendations");
    }
  }

  /**
   * Get a specific recommendation section by ID.
   * 
   * @param id - The section ID to look up
   * @returns Promise<RecommendationSection | undefined> - The section if found
   * 
   * @example
   * ```ts
   * const section = await recommendationService.getRecommendationSection("recommended");
   * console.log(section?.title); // "Recommended for You"
   * ```
   */
  async getRecommendationSection(id: string): Promise<RecommendationSection | undefined> {
    if (!id || id.trim().length === 0) {
      throw new Error("Invalid section ID");
    }

    try {
      // In production, this would be an API call:
      // const response = await fetch(`/api/recommendations/${id}`);
      // return response.json();
      const section = getRecommendationSection(id);
      
      if (section) {
        // Filter invalid books from this section
        return {
          ...section,
          books: section.books
            .map(book => this.safeCreateRecommendation(book))
            .filter((book): book is RecommendationBook => book !== null),
        };
      }
      
      return section;
    } catch (error) {
      console.error(`Error fetching recommendation section with ID ${id}:`, error);
      throw new Error(`Failed to fetch recommendation section with ID ${id}`);
    }
  }

  /**
   * Get all recommendation books across all sections.
   * 
   * @returns Promise<RecommendationBook[]> - Array of all recommendation books
   * 
   * @example
   * ```ts
   * const allBooks = await recommendationService.getAllRecommendationBooks();
   * console.log(allBooks.length); // Total recommended books
   * ```
   */
  async getAllRecommendationBooks(): Promise<RecommendationBook[]> {
    try {
      const books = getAllRecommendationBooks();
      return books
        .map(book => this.safeCreateRecommendation(book))
        .filter((book): book is RecommendationBook => book !== null);
    } catch (error) {
      console.error("Error fetching all recommendation books:", error);
      throw new Error("Failed to fetch all recommendation books");
    }
  }

  /**
   * Get the highest scored recommendation across all sections.
   * 
   * @returns Promise<RecommendationBook | undefined> - The highest scored recommendation
   * 
   * @example
   * ```ts
   * const top = await recommendationService.getHighestScoredRecommendation();
   * console.log(top?.title); // Highest scored book
   * ```
   */
  async getHighestScoredRecommendation(): Promise<RecommendationBook | undefined> {
    try {
      return getHighestScoredRecommendation();
    } catch (error) {
      console.error("Error fetching highest scored recommendation:", error);
      throw new Error("Failed to fetch highest scored recommendation");
    }
  }

  /**
   * Get recommendations by algorithm type.
   * 
   * @param algorithm - The algorithm to filter by
   * @returns Promise<RecommendationBook[]> - Filtered recommendations
   * 
   * @example
   * ```ts
   * const collaborative = await recommendationService.getRecommendationsByAlgorithm("collaborative");
   * console.log(collaborative); // Collaborative recommendations
   * ```
   */
  async getRecommendationsByAlgorithm(
    algorithm: RecommendationAlgorithm
  ): Promise<RecommendationBook[]> {
    try {
      return getRecommendationsByAlgorithm(algorithm);
    } catch (error) {
      console.error(`Error fetching recommendations by algorithm "${algorithm}":`, error);
      throw new Error(`Failed to fetch recommendations by algorithm "${algorithm}"`);
    }
  }

  /**
   * Get recommendations with high confidence.
   * 
   * @returns Promise<RecommendationBook[]> - High confidence recommendations
   * 
   * @example
   * ```ts
   * const highConfidence = await recommendationService.getHighConfidenceRecommendations();
   * console.log(highConfidence); // High confidence recommendations
   * ```
   */
  async getHighConfidenceRecommendations(): Promise<RecommendationBook[]> {
    try {
      return getHighConfidenceRecommendations();
    } catch (error) {
      console.error("Error fetching high confidence recommendations:", error);
      throw new Error("Failed to fetch high confidence recommendations");
    }
  }

  /**
   * Get featured recommendation sections.
   * 
   * @returns Promise<RecommendationSection[]> - Featured sections
   * 
   * @example
   * ```ts
   * const featured = await recommendationService.getFeaturedSections();
   * console.log(featured); // Featured sections
   * ```
   */
  async getFeaturedSections(): Promise<RecommendationSection[]> {
    try {
      return getFeaturedSections();
    } catch (error) {
      console.error("Error fetching featured sections:", error);
      throw new Error("Failed to fetch featured sections");
    }
  }

  /**
   * Get a random recommendation.
   * 
   * @returns Promise<RecommendationBook | undefined> - A random recommendation
   * 
   * @example
   * ```ts
   * const random = await recommendationService.getRandomRecommendation();
   * console.log(random?.title); // Random recommended book
   * ```
   */
  async getRandomRecommendation(): Promise<RecommendationBook | undefined> {
    try {
      return getRandomRecommendation();
    } catch (error) {
      console.error("Error fetching random recommendation:", error);
      throw new Error("Failed to fetch random recommendation");
    }
  }

  /**
   * Get the average recommendation score.
   * 
   * @returns Promise<number> - Average score
   * 
   * @example
   * ```ts
   * const avgScore = await recommendationService.getAverageRecommendationScore();
   * console.log(avgScore); // Average recommendation score
   * ```
   */
  async getAverageRecommendationScore(): Promise<number> {
    try {
      return getAverageRecommendationScore();
    } catch (error) {
      console.error("Error fetching average recommendation score:", error);
      throw new Error("Failed to fetch average recommendation score");
    }
  }

  /**
   * Get recommendation statistics.
   * 
   * @returns Promise<Object> - Recommendation statistics
   * 
   * @example
   * ```ts
   * const stats = await recommendationService.getRecommendationStats();
   * console.log(stats.totalRecommendations); // Total recommendations
   * ```
   */
  async getRecommendationStats() {
    try {
      return getRecommendationStats();
    } catch (error) {
      console.error("Error fetching recommendation stats:", error);
      throw new Error("Failed to fetch recommendation stats");
    }
  }

  /**
   * Get top N recommendations by score.
   * 
   * @param limit - Maximum number of recommendations to return (default: 5)
   * @returns Promise<RecommendationBook[]> - Top recommendations
   * 
   * @example
   * ```ts
   * const top5 = await recommendationService.getTopRecommendations(5);
   * console.log(top5); // Top 5 recommendations
   * ```
   */
  async getTopRecommendations(limit: number = 5): Promise<RecommendationBook[]> {
    if (limit <= 0) {
      return [];
    }

    try {
      return getTopRecommendations(limit);
    } catch (error) {
      console.error(`Error fetching top ${limit} recommendations:`, error);
      throw new Error(`Failed to fetch top ${limit} recommendations`);
    }
  }

  /**
   * Check if a book is recommended.
   * 
   * @param bookId - The book ID to check
   * @returns Promise<boolean> - True if the book is recommended
   * 
   * @example
   * ```ts
   * const isRecommended = await recommendationService.isBookRecommended(1);
   * console.log(isRecommended); // true or false
   * ```
   */
  async isBookRecommended(bookId: number): Promise<boolean> {
    if (!bookId || bookId <= 0) {
      return false;
    }

    try {
      return isBookRecommended(bookId);
    } catch (error) {
      console.error(`Error checking if book ${bookId} is recommended:`, error);
      return false;
    }
  }

  /**
   * Get the display label for a recommendation algorithm.
   * 
   * @param algorithm - The algorithm
   * @returns string - Human-readable label
   * 
   * @example
   * ```ts
   * const label = recommendationService.getAlgorithmLabel("collaborative");
   * console.log(label); // "Based on Your Taste"
   * ```
   */
  getAlgorithmLabel(algorithm: RecommendationAlgorithm): string {
    return getAlgorithmLabel(algorithm);
  }

  /**
   * Get the display label for a confidence level.
   * 
   * @param confidence - The confidence level
   * @returns string - Human-readable label
   * 
   * @example
   * ```ts
   * const label = recommendationService.getConfidenceLabel("high");
   * console.log(label); // "High Confidence"
   * ```
   */
  getConfidenceLabel(confidence: RecommendationConfidence): string {
    return getConfidenceLabel(confidence);
  }

  /**
   * Get the color class for a confidence level.
   * 
   * @param confidence - The confidence level
   * @returns string - CSS class for the color
   * 
   * @example
   * ```ts
   * const color = recommendationService.getConfidenceColor("high");
   * console.log(color); // "text-emerald-500 bg-emerald-500/10"
   * ```
   */
  getConfidenceColor(confidence: RecommendationConfidence): string {
    return getConfidenceColor(confidence);
  }

  /**
   * Filter recommendations by minimum score.
   * 
   * @param books - The books to filter
   * @param minScore - Minimum score (default: 50)
   * @returns RecommendationBook[] - Filtered recommendations
   * 
   * @example
   * ```ts
   * const filtered = await recommendationService.filterByMinScore(allBooks, 70);
   * console.log(filtered); // Books with score >= 70
   * ```
   */
  filterByMinScore(books: RecommendationBook[], minScore: number = 50): RecommendationBook[] {
    if (minScore < 0 || minScore > 100) {
      throw new Error("Invalid minimum score. Must be between 0 and 100");
    }

    try {
      return filterByMinScore(books, minScore);
    } catch (error) {
      console.error("Error filtering recommendations by min score:", error);
      throw new Error("Failed to filter recommendations by min score");
    }
  }

  /**
   * Sort recommendations by score (highest first).
   * 
   * @param books - The books to sort
   * @returns RecommendationBook[] - Sorted recommendations
   * 
   * @example
   * ```ts
   * const sorted = await recommendationService.sortByScore(allBooks);
   * console.log(sorted); // Books sorted by score descending
   * ```
   */
  sortByScore(books: RecommendationBook[]): RecommendationBook[] {
    try {
      return sortByScore(books);
    } catch (error) {
      console.error("Error sorting recommendations by score:", error);
      throw new Error("Failed to sort recommendations by score");
    }
  }
}

// ============================================================
// 📦 Export Singleton Instance
// ============================================================

export const recommendationService = new RecommendationService();