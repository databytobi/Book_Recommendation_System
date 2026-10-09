/**
 * ================================================================
 * 💡 Recommendation Types
 * ================================================================
 *
 * These types define the recommendation system's data structures.
 * They handle:
 * - Recommendation algorithms
 * - Confidence levels
 * - Recommended books
 * - Recommendation sections
 * ================================================================
 */

import { Book } from "./book";

// ============================================================
// 🤖 Recommendation Algorithms
// ============================================================

/**
 * Recommendation algorithms supported by the system.
 *
 * As the recommendation engine grows, new algorithms can
 * be added here without changing the RecommendationBook model.
 */
export type RecommendationAlgorithm =
  /** Most popular books based on overall ratings and views */
  | "popularity"
  
  /** Books with similar content (genres, themes, etc.) */
  | "content"
  
  /** Based on user behavior and preferences */
  | "collaborative"
  
  /** Combination of multiple algorithms for better results */
  | "hybrid"
  
  /** Books similar to a specific book */
  | "similar";

// ============================================================
// 📊 Recommendation Confidence
// ============================================================

/**
 * Recommendation confidence level.
 *
 * Used to describe how confident the system is
 * about recommending a particular book.
 */
export type RecommendationConfidence =
  /** Low confidence - user may or may not like this */
  | "low"
  
  /** Medium confidence - reasonable chance user will like this */
  | "medium"
  
  /** High confidence - strong match based on user preferences */
  | "high";

// ============================================================
// 📚 Recommended Book
// ============================================================

/**
 * A recommended book.
 *
 * Extends the base Book model with recommendation-specific
 * information produced by the recommendation engine.
 * 
 * ✅ This is the only place RecommendationBook is defined.
 * If it's also defined in book.ts, remove it from there.
 */
export interface RecommendationBook extends Book {
  /**
   * Recommendation score (0–100).
   * Higher score means better match for the user.
   */
  score: number;

  /**
   * Human-readable explanation shown in the UI.
   * Explains why this book was recommended.
   */
  reason: string;

  /**
   * Algorithm responsible for this recommendation.
   * Helps users understand where the recommendation came from.
   */
  algorithm: RecommendationAlgorithm;

  /**
   * Confidence assigned by the recommendation engine.
   * Indicates how reliable the recommendation is.
   */
  confidence?: RecommendationConfidence;

  /**
   * Ranking position in the recommendation list (1-based).
   */
  rank?: number;

  /**
   * Whether the user has already seen this recommendation.
   */
  seen?: boolean;

  /**
   * Whether the user has interacted with this recommendation.
   */
  interacted?: boolean;

  /**
   * Timestamp when the recommendation was generated.
   */
  recommendedAt?: string;
}

// ============================================================
// 📋 Recommendation Section
// ============================================================

/**
 * A recommendation section displayed on the dashboard
 * or recommendations page.
 *
 * Example:
 * - Recommended For You
 * - Because You Read Dune
 * - Trending This Week
 */
export interface RecommendationSection {
  /** Unique identifier for the section */
  id: string;

  /** Display title of the section */
  title: string;

  /** Optional description explaining the section */
  description?: string;

  /** List of recommended books in this section */
  books: RecommendationBook[];

  /** Icon or emoji to display with the section */
  icon?: string;

  /** Color scheme for the section */
  color?: "blue" | "purple" | "emerald" | "amber" | "rose";

  /** Whether the section is featured (prominently displayed) */
  featured?: boolean;

  /** Total number of books in this section (for pagination) */
  total?: number;

  /** Link to view all books in this section */
  viewAllLink?: string;
}

// ============================================================
// 🏗️ Factory Functions
// ============================================================

/**
 * Create a recommendation book from a base book.
 */
export function createRecommendationBook(params: {
  book: Book;
  score: number;
  reason: string;
  algorithm: RecommendationAlgorithm;
  confidence?: RecommendationConfidence;
  rank?: number;
}): RecommendationBook {
  // ✅ Ensure score is a number
  const score = typeof params.score === 'number' ? params.score : Number(params.score) || 0;
  
  return {
    ...params.book,
    score: Math.min(Math.max(score, 0), 100),
    reason: params.reason,
    algorithm: params.algorithm,
    confidence: params.confidence || "medium",
    rank: params.rank,
    seen: false,
    interacted: false,
    recommendedAt: new Date().toISOString(),
  };
}

/**
 * Create a recommendation section.
 */
export function createRecommendationSection(params: {
  id: string;
  title: string;
  description?: string;
  books: RecommendationBook[];
  icon?: string;
  color?: "blue" | "purple" | "emerald" | "amber" | "rose";
  featured?: boolean;
  total?: number;
  viewAllLink?: string;
}): RecommendationSection {
  return {
    id: params.id,
    title: params.title,
    description: params.description,
    books: params.books,
    icon: params.icon,
    color: params.color || "blue",
    featured: params.featured || false,
    total: params.total || params.books.length,
    viewAllLink: params.viewAllLink,
  };
}

// ============================================================
// 🔄 Helper Functions
// ============================================================

/**
 * Get the display label for a recommendation algorithm.
 */
export function getAlgorithmLabel(algorithm: RecommendationAlgorithm): string {
  const labels: Record<RecommendationAlgorithm, string> = {
    popularity: "Popular",
    content: "Similar Content",
    collaborative: "Based on Your Taste",
    hybrid: "Smart Match",
    similar: "Similar Books",
  };
  return labels[algorithm] || algorithm;
}

/**
 * Get the display color for a confidence level.
 */
export function getConfidenceColor(confidence: RecommendationConfidence): string {
  const colors: Record<RecommendationConfidence, string> = {
    high: "text-emerald-500 bg-emerald-500/10",
    medium: "text-amber-500 bg-amber-500/10",
    low: "text-muted-foreground bg-muted/50",
  };
  return colors[confidence] || "text-muted-foreground bg-muted/50";
}

/**
 * Get the display label for a confidence level.
 */
export function getConfidenceLabel(confidence: RecommendationConfidence): string {
  const labels: Record<RecommendationConfidence, string> = {
    high: "High Confidence",
    medium: "Medium Confidence",
    low: "Low Confidence",
  };
  return labels[confidence] || confidence;
}

/**
 * Get the display color for a section.
 */
export function getSectionColor(color: RecommendationSection["color"]): string {
  const colors = {
    blue: "border-blue-500/30 bg-blue-500/5",
    purple: "border-purple-500/30 bg-purple-500/5",
    emerald: "border-emerald-500/30 bg-emerald-500/5",
    amber: "border-amber-500/30 bg-amber-500/5",
    rose: "border-rose-500/30 bg-rose-500/5",
  };
  return colors[color || "blue"] || colors.blue;
}

/**
 * Filter recommendations by confidence level.
 */
export function filterByConfidence(
  books: RecommendationBook[],
  confidence: RecommendationConfidence
): RecommendationBook[] {
  return books.filter(book => book.confidence === confidence);
}

/**
 * Get top N recommendations by score.
 * ✅ Handles null/undefined scores safely
 */
export function getTopRecommendations(
  books: RecommendationBook[],
  limit: number = 5
): RecommendationBook[] {
  return [...books]
    .sort((a, b) => (b.score || 0) - (a.score || 0))
    .slice(0, limit);
}

/**
 * Get recommendations by algorithm.
 */
export function getRecommendationsByAlgorithm(
  books: RecommendationBook[],
  algorithm: RecommendationAlgorithm
): RecommendationBook[] {
  return books.filter(book => book.algorithm === algorithm);
}

/**
 * Calculate the average score of recommendations.
 * ✅ Renamed to avoid conflict with search.ts
 */
export function getAverageRecommendationScore(books: RecommendationBook[]): number {
  if (books.length === 0) return 0;
  const validScores = books
    .map(book => book.score)
    .filter((score): score is number => score !== undefined && score !== null);
  if (validScores.length === 0) return 0;
  const total = validScores.reduce((sum, score) => sum + score, 0);
  return Math.round(total / validScores.length);
}

/**
 * Get the highest scored recommendation.
 * ✅ Handles null/undefined scores safely
 */
export function getHighestScored(books: RecommendationBook[]): RecommendationBook | null {
  if (books.length === 0) return null;
  return books.reduce((best, current) => {
    const bestScore = best.score || 0;
    const currentScore = current.score || 0;
    return currentScore > bestScore ? current : best;
  });
}

/**
 * Check if a book is recommended.
 */
export function isRecommended(book: Book): book is RecommendationBook {
  return (book as RecommendationBook).score !== undefined;
}

/**
 * Get a summary of recommendations by algorithm.
 */
export function getAlgorithmSummary(books: RecommendationBook[]): Array<{
  algorithm: RecommendationAlgorithm;
  label: string;
  count: number;
  averageScore: number;
}> {
  const algorithmMap = new Map<RecommendationAlgorithm, RecommendationBook[]>();
  
  books.forEach(book => {
    if (!algorithmMap.has(book.algorithm)) {
      algorithmMap.set(book.algorithm, []);
    }
    algorithmMap.get(book.algorithm)!.push(book);
  });

  return Array.from(algorithmMap.entries()).map(([algorithm, books]) => ({
    algorithm,
    label: getAlgorithmLabel(algorithm),
    count: books.length,
    averageScore: getAverageRecommendationScore(books),
  }));
}

/**
 * ✅ New helper: Get recommendations with high confidence
 */
export function getHighConfidenceRecommendations(
  books: RecommendationBook[]
): RecommendationBook[] {
  return books.filter(book => book.confidence === "high");
}

/**
 * ✅ New helper: Get recommendation statistics
 */
export function getRecommendationStats(books: RecommendationBook[]) {
  const total = books.length;
  const avgScore = getAverageRecommendationScore(books);
  const highConfidence = books.filter(b => b.confidence === "high").length;
  const algorithms = books.reduce((acc, book) => {
    const alg = book.algorithm || "unknown";
    acc[alg] = (acc[alg] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return {
    totalRecommendations: total,
    averageScore: avgScore,
    highConfidenceCount: highConfidence,
    algorithmDistribution: algorithms,
  };
}

/**
 * ✅ New helper: Sort recommendations by score
 */
export function sortByScore(books: RecommendationBook[]): RecommendationBook[] {
  return [...books].sort((a, b) => (b.score || 0) - (a.score || 0));
}