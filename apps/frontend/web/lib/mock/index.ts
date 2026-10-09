// apps/frontend/web/lib/mock/index.ts

// ============================================================
// 📚 Book Mock Data
// ============================================================
export {
  books,
  getBookById,
  getBooksByAuthor,
  getBooksByYear,
  getBooksByRating,
  getTopRatedBooks,
  getRecentBooks,
  searchBooks as searchBooksFromBooks, // ✅ Aliased to avoid conflict
  getRandomBooks,
  getBookStats,
  formatBookDisplay,
  isHighlyRated,
} from "./books";

// ============================================================
// 🔍 Search Mock Data
// ============================================================
export {
  searchHistory,
  popularSearches,
  mockSearchResponse,
  searchBooks, // ✅ This is the main search function
  getSearchHistory,
  getPopularSearches,
   getSearchHistoryItem,
  addSearchToHistory,
  clearSearchHistory,
  removeSearchFromHistory,
  getRecentSearches,
  getPopularSearchesByCategory,
  getTrendingSearches,
  getSearchStats,
  formatSearchTime,
  getResultCountMessage,
  hasSearchResults,
  getPaginationDisplay,
  // ...
} from "./search";

// lib/mock/index.ts

// ... other exports ...

// 📖 Reading Mock Data
export {
  continueReadingBooks,
  recentlyViewedBooks,
  readingHistory,
  readingGoals,
  getContinueReadingBooks,    // ✅ Make sure this is exported
  getRecentlyViewedBooks,     // ✅ Make sure this is exported
  getReadingHistory,          // ✅ Make sure this is exported
  getReadingGoals,
  getPrimaryReadingGoal,
  getInProgressBooks,
  getCompletedBooks,
  getTotalPagesRead,
  getAverageProgress,
  getMostRecentView,
  getReadingHistoryByYear,
  getCompletedHistoryItems,
  getReadingStats,
} from "./reading";

// 💡 Recommendation Mock Data
export {
  recommendedForYou,
  becauseYouRead,
  trendingBooks,
  recommendationSections,
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
  formatRecommendation,
  isBookRecommended,
  getAlgorithmLabel,
  getConfidenceLabel,
  getConfidenceColor,
  filterByMinScore,
  sortByScore,
} from "./recommendations";  // ✅ Use "recommendation" (singular)

export { currentUser, getCurrentUser } from "./users";

export {
  getDashboardData,
  getDashboardStats,
  getDashboardStat,
  getPrimaryStat,
  getPositiveTrendStats,
  getNegativeTrendStats,
  getOverallProgress,
  formatStatValue,
  getTrendColor,
  getStatIconName,
  hasDashboardData,
  getDashboardSummary,
  getRecentActivity,
  getDashboardStatus,
} from "./dashboard";