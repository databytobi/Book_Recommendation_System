/**
 * ================================================================
 * 📊 Dashboard Mock Data
 * ================================================================
 *
 * This file contains mock dashboard data for development and testing.
 * It represents:
 * - Dashboard statistics (key metrics)
 * - Continue reading books
 * - Recently viewed books
 * - Recommendation sections
 * - Reading goals
 *
 * IMPORTANT: This is mock data and should be replaced with
 * real API data in production.
 * ================================================================
 */

import type { DashboardData, DashboardStat } from "@/lib/types";

import {
  continueReadingBooks as continueReading,
  readingGoals,
  recentlyViewedBooks as recentlyViewed,
} from "./reading";
import { recommendationSections } from "./recommendations";

// ============================================================
// 📈 Dashboard Statistics - ONLY 4 STATS (No Duplicates)
// ============================================================

export const dashboardStats: DashboardStat[] = [
  {
    id: "books-read",
    title: "Books Read",
    value: 48,
    change: 12,
    description: "Compared to last month",
    icon: "bookOpen",
    trend: "up",
    variant: "primary",
  },
  {
    id: "reading-streak",
    title: "reading streak",
    value: "14 Days",
    change: 2,
    description: "Keep it going!",
    icon: "flame",
    trend: "up",
    variant: "success",
  },
  {
    id: "saved-books",
    title: "saved books",
    value: 17,
    change: -3,
    description: "Your reading list",
    icon: "bookmark",
    trend: "down",
    variant: "warning",
  },
  {
    id: "pages-read",
    title: "Pages Read",
    value: "16,872",
    change: 18,
    description: "Total pages completed",
    icon: "library",
    trend: "up",
    variant: "default",
  },
];

// ============================================================
// 📊 Complete Dashboard Data
// ============================================================

export const dashboardData: DashboardData = {
  stats: dashboardStats,
  continueReading,
  recentlyViewed,
  recommendations: recommendationSections,
  readingGoal: readingGoals[0],
  lastUpdated: new Date().toISOString(),
  welcomeMessage: "Welcome back, Bruno!",
  readingStreak: 14,
  totalBooks: 68,
  booksCompletedThisYear: 32,
};

// ============================================================
// 🔄 Dashboard Helper Functions
// ============================================================

export function getDashboardData(): DashboardData {
  return dashboardData;
}

export function getDashboardStats(): DashboardStat[] {
  return dashboardStats;
}

export function getDashboardStat(title: string): DashboardStat | undefined {
  return dashboardStats.find((stat) => stat.title === title);
}

export function getPrimaryStat(): DashboardStat | undefined {
  return dashboardStats[0];
}

export function getPositiveTrendStats(): DashboardStat[] {
  return dashboardStats.filter((stat) => stat.trend === "up");
}

export function getNegativeTrendStats(): DashboardStat[] {
  return dashboardStats.filter((stat) => stat.trend === "down");
}

export function getOverallProgress(): number {
  const total = dashboardStats.length;
  const positive = dashboardStats.filter(
    (stat) => stat.trend === "up" || (stat.change && stat.change > 0)
  ).length;
  return Math.round((positive / total) * 100);
}

export function formatStatValue(stat: DashboardStat): string {
  if (typeof stat.value === "string") {
    return stat.value;
  }
  if (typeof stat.value === "number") {
    if (stat.value >= 1000) {
      return `${(stat.value / 1000).toFixed(1)}k`;
    }
    return stat.value.toString();
  }
  return String(stat.value);
}

export function getTrendColor(stat: DashboardStat): string {
  if (stat.trend === "up") return "text-emerald-500";
  if (stat.trend === "down") return "text-rose-500";
  return "text-muted-foreground";
}

export function getStatIconName(stat: DashboardStat): string {
  const iconMap: Record<string, string> = {
    BookOpen: "📖",
    Flame: "🔥",
    Bookmark: "🔖",
    Library: "📚",
    Clock: "⏰",
    Star: "⭐",
  };
  return iconMap[stat.icon || ""] || "📊";
}

export function hasDashboardData(): boolean {
  return (
    dashboardStats.length > 0 ||
    continueReading.length > 0 ||
    recentlyViewed.length > 0 ||
    recommendationSections.length > 0
  );
}

export function getDashboardSummary() {
  const totalBooks = dashboardStats.find((s) => s.title === "Books Read")?.value || 0;
  const streak = dashboardStats.find((s) => s.title === "reading streak")?.value || "0";
  const pages = dashboardStats.find((s) => s.title === "Pages Read")?.value || "0";

  return {
    totalBooksRead: typeof totalBooks === "number" ? totalBooks : 0,
    readingStreak: typeof streak === "string" ? streak : "0",
    totalPagesRead: typeof pages === "string" ? pages : "0",
    recommendationCount: recommendationSections.reduce(
      (acc, section) => acc + section.books.length,
      0
    ),
    booksInProgress: continueReading.length,
  };
}

export function getRecentActivity() {
  const activities = [];

  if (continueReading.length > 0) {
    const book = continueReading[0];
    const progress = book.progress?.percentage || 0;
    activities.push({
      type: "reading",
      message: `Reading "${book.title}"`,
      details: `${progress}% complete`,
      timestamp: book.progress?.lastReadAt || new Date().toISOString(),
    });
  }

  if (recentlyViewed.length > 0) {
    const book = recentlyViewed[0];
    activities.push({
      type: "viewed",
      message: `Viewed "${book.title}"`,
      details: "Recently viewed",
      timestamp: book.viewedAt || new Date().toISOString(),
    });
  }

  if (recommendationSections.length > 0) {
    const section = recommendationSections[0];
    if (section.books.length > 0) {
      const book = section.books[0];
      activities.push({
        type: "recommended",
        message: `Recommended "${book.title}"`,
        details: book.reason || "Based on your reading history",
        timestamp: book.recommendedAt || new Date().toISOString(),
      });
    }
  }

  return activities.sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );
}

export function getDashboardStatus() {
  return {
    isDataLoaded: true,
    lastUpdated: dashboardData.lastUpdated,
    isStale: false,
    dataFreshness: "fresh",
  };
}