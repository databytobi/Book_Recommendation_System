// apps/frontend/web/lib/mock/recommendations.ts

/**
 * ================================================================
 * 💡 Recommendation Mock Data
 * ================================================================
 *
 * This file contains mock recommendation data for development and testing.
 * It represents:
 * - Personalized recommendations
 * - "Because You Read" recommendations
 * - Trending books
 * - Recommendation sections with scores and explanations
 *
 * IMPORTANT: This is mock data and should be replaced with
 * real API data in production.
 * ================================================================
 */

import type {
  RecommendationBook,
  RecommendationSection,
  RecommendationAlgorithm,
  RecommendationConfidence,
} from "@/lib/types";

// FIX: Removed unused 'books' import
import { getBookById } from "./books";

// ============================================================
// 🔧 Extended Type (for internal use)
// ============================================================

interface ExtendedRecommendationBook extends RecommendationBook {
  algorithm: RecommendationAlgorithm;
  confidence?: RecommendationConfidence;
}

// ============================================================
// 🎯 Recommendation Builders
// ============================================================

function createRecommendation(
  bookId: number,
  score: number,
  reason: string,
  algorithm: RecommendationAlgorithm,
  confidence: RecommendationConfidence = "medium"
): ExtendedRecommendationBook {
  const book = getBookById(bookId);
  if (!book) {
    throw new Error(`Book with ID ${bookId} not found`);
  }
  
  return {
    ...book,
    score: Math.min(Math.max(score, 0), 100),
    reason,
    algorithm,
    confidence,
  } as ExtendedRecommendationBook;
}

// ============================================================
// 💡 Recommendation Sections
// ============================================================

export const recommendedForYou: RecommendationSection = {
  id: "recommended",
  title: "Recommended for You",
  description: "Books selected based on your reading history.",
  icon: "🎯",
  color: "purple",
  featured: true,
  total: 2,
  viewAllLink: "/recommendations/recommended",
  books: [
    // ✅ FIXED: Changed ID from 0 to 1 (valid book ID)
    createRecommendation(1, 98, "Because you enjoy productivity books.", "hybrid", "high"),
    createRecommendation(3, 95, "Readers with similar interests loved this.", "collaborative", "high"),
  ],
};

export const becauseYouRead: RecommendationSection = {
  id: "because-atomic-habits",
  title: "Because You Read Atomic Habits",
  description: "More books that complement your recent reading.",
  icon: "📚",
  color: "emerald",
  featured: false,
  total: 2,
  viewAllLink: "/recommendations/because-atomic-habits",
  books: [
    createRecommendation(1, 94, "Similar themes and writing style.", "content", "high"),
    createRecommendation(4, 92, "Frequently read by Atomic Habits readers.", "hybrid", "medium"),
  ],
};

export const trendingBooks: RecommendationSection = {
  id: "trending",
  title: "Trending This Week",
  description: "Popular among readers this week.",
  icon: "🔥",
  color: "rose",
  featured: false,
  total: 2,
  viewAllLink: "/recommendations/trending",
  books: [
    createRecommendation(2, 90, "Currently trending worldwide.", "popularity", "high"),
    createRecommendation(4, 88, "Highly rated by the community.", "popularity", "medium"),
  ],
};

export const recommendationSections: RecommendationSection[] = [
  recommendedForYou,
  becauseYouRead,
  trendingBooks,
];

// ============================================================
// 🔄 Helper Functions
// ============================================================

export function getRecommendations(): RecommendationSection[] {
  return recommendationSections;
}

export function getRecommendationSection(id: string): RecommendationSection | undefined {
  return recommendationSections.find((section) => section.id === id);
}

export function getAllRecommendationBooks(): ExtendedRecommendationBook[] {
  return recommendationSections.flatMap((section) => section.books) as ExtendedRecommendationBook[];
}

export function getHighestScoredRecommendation(): ExtendedRecommendationBook | undefined {
  const allBooks = getAllRecommendationBooks();
  if (allBooks.length === 0) return undefined;
  return allBooks.reduce((best, current) => {
    const bestScore = best.score || 0;
    const currentScore = current.score || 0;
    return currentScore > bestScore ? current : best;
  });
}

export function getRecommendationsByAlgorithm(
  algorithm: RecommendationAlgorithm
): ExtendedRecommendationBook[] {
  return getAllRecommendationBooks().filter(
    (book) => book.algorithm === algorithm
  );
}

export function getHighConfidenceRecommendations(): ExtendedRecommendationBook[] {
  return getAllRecommendationBooks().filter(
    (book) => book.confidence === "high"
  );
}

export function getFeaturedSections(): RecommendationSection[] {
  return recommendationSections.filter((section) => section.featured);
}

export function getRandomRecommendation(): ExtendedRecommendationBook | undefined {
  const allBooks = getAllRecommendationBooks();
  if (allBooks.length === 0) return undefined;
  return allBooks[Math.floor(Math.random() * allBooks.length)];
}

export function getAverageRecommendationScore(): number {
  const allBooks = getAllRecommendationBooks();
  if (allBooks.length === 0) return 0;
  const validScores = allBooks
    .map((book) => book.score)
    .filter((score): score is number => score !== undefined && score !== null);
  if (validScores.length === 0) return 0;
  const total = validScores.reduce((sum, score) => sum + score, 0);
  return Math.round(total / validScores.length);
}

export function getRecommendationStats() {
  const allBooks = getAllRecommendationBooks();
  const total = allBooks.length;
  const avgScore = getAverageRecommendationScore();
  const highConfidence = allBooks.filter((b) => b.confidence === "high").length;
  const algorithms = allBooks.reduce((acc, book) => {
    const alg = book.algorithm || "unknown";
    acc[alg] = (acc[alg] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return {
    totalRecommendations: total,
    averageScore: avgScore,
    highConfidenceCount: highConfidence,
    algorithmDistribution: algorithms,
    sections: recommendationSections.length,
  };
}

export function getTopRecommendations(limit: number = 5): ExtendedRecommendationBook[] {
  return getAllRecommendationBooks()
    .sort((a, b) => (b.score || 0) - (a.score || 0))
    .slice(0, limit);
}

export function formatRecommendation(book: ExtendedRecommendationBook): string {
  const score = book.score !== undefined && book.score !== null ? book.score : 0;
  return `${book.title} by ${book.author.name} (${score}% match) - ${book.reason || "Recommended"}`;
}

export function isBookRecommended(bookId: number): boolean {
  return getAllRecommendationBooks().some((book) => book.id === bookId);
}

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

export function getConfidenceLabel(confidence: RecommendationConfidence): string {
  const labels: Record<RecommendationConfidence, string> = {
    high: "High Confidence",
    medium: "Medium Confidence",
    low: "Low Confidence",
  };
  return labels[confidence] || confidence;
}

export function getConfidenceColor(confidence: RecommendationConfidence): string {
  const colors: Record<RecommendationConfidence, string> = {
    high: "text-emerald-500 bg-emerald-500/10",
    medium: "text-amber-500 bg-amber-500/10",
    low: "text-muted-foreground bg-muted/50",
  };
  return colors[confidence] || "text-muted-foreground bg-muted/50";
}

// ✅ ADDED: Filter recommendations by minimum score
export function filterByMinScore(
  books: ExtendedRecommendationBook[],
  minScore: number = 50
): ExtendedRecommendationBook[] {
  return books.filter((book) => (book.score || 0) >= minScore);
}

// ✅ ADDED: Sort recommendations by score (highest first)
export function sortByScore(books: ExtendedRecommendationBook[]): ExtendedRecommendationBook[] {
  return [...books].sort((a, b) => (b.score || 0) - (a.score || 0));
}