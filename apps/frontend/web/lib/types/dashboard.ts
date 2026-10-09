/**
 * ================================================================
 * 📊 Dashboard Types
 * ================================================================
 *
 * These types define the data structure for the user's dashboard.
 * The dashboard is the main landing page after authentication.
 *
 * It displays:
 * - Key statistics (books read, reading streak, etc.)
 * - Continue reading section
 * - Recently viewed books
 * - Personalized recommendations
 * - Reading goal progress
 * ================================================================
 */


import type { RecommendationSection } from "./recommendation";
import type {
  ContinueReadingBook,
  RecentlyViewedBook,
  ReadingGoal,
} from "./reading";

// ============================================================
// 📈 Dashboard Statistics
// ============================================================

/**
 * Statistic displayed at the top of the dashboard.
 * 
 * These are key metrics that give users a quick overview
 * of their reading activity and progress.
 */

export type DashboardStatIcon =
  | "bookOpen"
  | "flame"
  | "bookmark"
  | "library"
  | "clock"
  | "star";

export interface DashboardStat {

  id: string;
  /** Display title of the statistic (e.g., "Books Read", "Reading Streak") */
  title: string;

  /** Primary value to display (e.g., "24", "12 days", "4.8★") */
  value: number | string;

  /** Percentage change compared to previous period (e.g., 12 for +12%) */
  change?: number;

  /** Additional context or description (e.g., "This month", "All time") */
  description?: string;

  /** Stable icon key used to map dashboard icons *(e.g., "book-open", "trending-up") */
  icon: DashboardStatIcon;

  /** Trend direction: up, down, or neutral */
  trend?: "up" | "down" | "neutral";

  /** Color variant for the stat card */
  variant?: "default" | "primary" | "success" | "warning" | "destructive";
}

// ============================================================
// 📊 Dashboard Data
// ============================================================

/**
 * Complete dashboard data.
 *
 * This represents everything needed to render the user's dashboard.
 * It's typically fetched from the API on page load and refreshed
 * periodically or on user action.
 */
export interface DashboardData {
  /** Key metrics and statistics for the user */
  stats: DashboardStat[];

  /** Books the user is currently reading with progress */
  continueReading: ContinueReadingBook[];

  /** Books the user has recently viewed */
  recentlyViewed: RecentlyViewedBook[];

  /** Personalized recommendation sections (e.g., "Recommended for You", "Trending") */
  recommendations: RecommendationSection[];

  /** User's reading goal and progress (if set) */
  readingGoal?: ReadingGoal;

  /** Timestamp when the dashboard data was last updated */
  lastUpdated?: string;

  /** Welcome message or greeting for the user */
  welcomeMessage?: string;

  /** User's current reading streak in days */
  readingStreak?: number;

  /** Total books in the user's library */
  totalBooks?: number;

  /** Books completed this year */
  booksCompletedThisYear?: number;
}

// ============================================================
// 🏗️ Factory Functions
// ============================================================

/**
 * Create a default dashboard stat.
 */
export function createDashboardStat(params: {
  id: string;
  title: string;
  value: number | string;
  change?: number;
  description?: string;
  icon: DashboardStatIcon;
  trend?: "up" | "down" | "neutral";
  variant?: "default" | "primary" | "success" | "warning" | "destructive";
}): DashboardStat {
  return {
    id: params.id,
    title: params.title,
    value: params.value,
    change: params.change,
    description: params.description,
    icon: params.icon,
    trend: params.trend || "neutral",
    variant: params.variant || "default",
  };
}

/**
 * Create an empty dashboard data object with default values.
 */
export function createEmptyDashboardData(): DashboardData {
  return {
    stats: [],
    continueReading: [],
    recentlyViewed: [],
    recommendations: [],
    readingGoal: undefined,
    lastUpdated: new Date().toISOString(),
    readingStreak: 0,
    totalBooks: 0,
    booksCompletedThisYear: 0,
  };
}

// ============================================================
// 🔄 Helper Functions
// ============================================================

/**
 * Check if the dashboard has any data to display.
 */
export function hasDashboardData(data: DashboardData): boolean {
  return (
    data.stats.length > 0 ||
    data.continueReading.length > 0 ||
    data.recentlyViewed.length > 0 ||
    data.recommendations.length > 0
  );
}

/**
 * Check if the dashboard is empty (no data at all).
 */
export function isDashboardEmpty(data: DashboardData): boolean {
  return !hasDashboardData(data);
}

/**
 * Get the total number of books across all sections.
 */
export function getTotalBooksInDashboard(data: DashboardData): number {
  return (
    data.continueReading.length +
    data.recentlyViewed.length +
    (data.totalBooks || 0)
  );
}

/**
 * Get the user's overall reading progress percentage.
 * 
 * Uses the ReadingGoal's progressPercentage field directly.
 * 
 * @param data - The dashboard data
 * @returns Percentage (0-100) or 0 if no reading goal
 */
export function getOverallReadingProgress(data: DashboardData): number {
  if (!data.readingGoal) return 0;
  
  // ✅ Use the existing progressPercentage from ReadingGoal
  return data.readingGoal.progressPercentage ?? 0;
}

/**
 * Get the remaining books/pages/minutes to reach the reading goal.
 */
export function getRemainingToGoal(data: DashboardData): number {
  if (!data.readingGoal) return 0;
  
  const { target, current } = data.readingGoal;
  return Math.max(target - current, 0);
}

/**
 * Get the reading goal completion message based on progress.
 */
export function getGoalCompletionMessage(data: DashboardData): string {
  if (!data.readingGoal) return "No reading goal set";
  
  const progress = data.readingGoal.progressPercentage ?? 0;
  
  if (progress >= 100) return "🎉 Goal achieved!";
  if (progress >= 75) return "🔥 Almost there!";
  if (progress >= 50) return "📚 Halfway there!";
  if (progress >= 25) return "💪 Great start!";
  return "🌟 Let's get started!";
}

/**
 * Get a formatted reading goal summary.
 */
export function getReadingGoalSummary(data: DashboardData): string {
  if (!data.readingGoal) return "Set a reading goal";
  
  const { goalType, target, current } = data.readingGoal;
  const label = goalType === "books" ? "books" : goalType === "pages" ? "pages" : "minutes";
  
  return `${current} / ${target} ${label}`;
}

/**
 * Get the reading goal type label.
 */
export function getReadingGoalTypeLabel(goal: ReadingGoal): string {
  switch (goal.goalType) {
    case "books":
      return "Books";
    case "pages":
      return "Pages";
    case "minutes":
      return "Minutes";
    default:
      return goal.goalType;
  }
}

/**
 * Check if the user has a reading goal set.
 */
export function hasReadingGoal(data: DashboardData): boolean {
  return !!data.readingGoal && data.readingGoal.target > 0;
}

/**
 * Get reading streak information.
 */
export function getReadingStreakInfo(data: DashboardData): {
  currentStreak: number;
  longestStreak: number;
  streakMessage: string;
} {
  if (!data.readingGoal) {
    return {
      currentStreak: 0,
      longestStreak: 0,
      streakMessage: "No streak data available",
    };
  }

  const { currentStreak, longestStreak } = data.readingGoal;
  
  let message = `${currentStreak} day${currentStreak !== 1 ? "s" : ""} streak`;
  if (currentStreak === 0) {
    message = "Start a streak today! 🔥";
  } else if (currentStreak === longestStreak) {
    message = `🔥 ${currentStreak} days - Best streak!`;
  }
  
  return {
    currentStreak,
    longestStreak,
    streakMessage: message,
  };
}