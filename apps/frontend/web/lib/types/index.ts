// lib/types/index.ts

// Export all types from individual files
export * from "./auth";
export * from "./book";
export * from "./common";
export * from "./dashboard";
export * from "./reading";
export * from "./search";
export * from "./user";

// Recommendation types with explicit exports (if you need specific naming)
export {
  type RecommendationAlgorithm,
  type RecommendationConfidence,
  type RecommendationBook,
  type RecommendationSection,
  createRecommendationBook,
  createRecommendationSection,
  getAlgorithmLabel,
  getConfidenceColor,
  getConfidenceLabel,
  getSectionColor,
  filterByConfidence,
  getTopRecommendations,
  getRecommendationsByAlgorithm,
  getAverageRecommendationScore,
  getHighestScored,
  isRecommended,
  getAlgorithmSummary,
  getHighConfidenceRecommendations,
  getRecommendationStats,
  sortByScore,
} from "./recommendation";