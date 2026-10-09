/**
 * ================================================================
 * 📊 Dashboard Service
 * ================================================================
 *
 * Handles all dashboard-related operations including:
 * - Getting complete dashboard data
 * - Getting dashboard statistics
 * - Getting specific dashboard stats
 * - Getting dashboard summary
 * - Getting recent activity
 * - Getting dashboard status
 *
 * Currently backed by mock data.
 * Will later communicate with the backend API.
 * ================================================================
 */

import {
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
} from "@/lib/mock";

import type {
  DashboardData,
  DashboardStat,
} from "@/lib/types";

import {
  getRecommendations,
  type RecommendedBook,
} from "@/lib/services/recommendationService";

// Step 1: Add API base and auth headers
const API_BASE = "http://127.0.0.1:8000/api/v1";

const authHeaders = () => ({
  Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
});

// ============================================================
// 📊 Dashboard Service Class
// ============================================================

class DashboardService {
  /**
   * Get complete dashboard data.
   * 
   * @returns Promise<DashboardData> - Complete dashboard data
   * 
   * @example
   * ```ts
   * const dashboard = await dashboardService.getDashboard();
   * console.log(dashboard.stats); // Dashboard statistics
   * ```
   */
  async getDashboard(): Promise<DashboardData> {
    try {
      // Start with empty dashboard
      const dashboard: DashboardData = {
        stats: [],
        continueReading: [],
        recentlyViewed: [],
        recommendations: [],
        readingGoal: undefined,
        lastUpdated: new Date().toISOString(),
        welcomeMessage: "Welcome back!",
        readingStreak: 0,
        totalBooks: 0,
        booksCompletedThisYear: 0,
      };

      // Fetch history and favorites in parallel.
      //
      // Recommendations are supplementary: if they fail, the dashboard must
      // still render stats/history/favorites with an empty recommendations
      // section. Previously this rejection propagated out of Promise.all,
      // failed the whole getDashboard() call, and the page showed
      // "Something went wrong while loading your dashboard."
      const [historyRes, favRes, recResponse] = await Promise.all([
        fetch(`${API_BASE}/history`, { headers: authHeaders() }),
        fetch(`${API_BASE}/favorites`, { headers: authHeaders() }),
        getRecommendations(20).catch((recError) => {
          console.error("Recommendations failed; showing dashboard without them:", recError);
          return { success: false, total: 0, generated_from: "hybrid", recommendations: [] };
        }),
      ]);

      const history = historyRes.ok ? await historyRes.json() : { history: [] };
      const favorites = favRes.ok ? await favRes.json() : { total: 0 };

      // -----------------------------
      // Stats - ALL stats now have IDs
      // -----------------------------
      dashboard.stats = [
        {
          id: "books-read",
          title: "Books Read",
          value: String(history.history?.length ?? 0),
          description: "Books you've completed",
          icon: "bookOpen",
        },
        {
          id: "reading-streak",
          title: "Reading Streak",
          value: String(0),
          description: "Keep going!",
          icon: "flame",
        },
        {
          id: "saved-books",
          title: "Saved Books",
          value: String(favorites.total ?? 0),
          description: "Books in your library",
          icon: "bookmark",
        },
        {
          id: "pages-read",
          title: "Pages Read",
          value: String(
            history.history?.reduce(
              (acc: number, book: any) => acc + (book.progress_percentage ?? 0),
              0
            ) ?? 0
          ),
          description: "Total pages completed",
          icon: "library",
        },
        {
          id: "reading-time",
          title: "Reading Time",
          value: "0h",
          description: "Total reading time",
          icon: "clock",
        },
        {
          id: "average-rating",
          title: "Average Rating",
          value: "4.3★",
          description: "Average rating given",
          icon: "star",
        },
      ];

      // -----------------------------
      // Continue Reading
      // -----------------------------
      const latest = history.history?.[0];

      dashboard.continueReading = latest
        ? [
            {
              id: latest.isbn || `book_${Date.now()}`,
              title: latest.title || 'Untitled Book',
              author: { 
                id: latest.author || 'unknown-author', 
                name: latest.author || 'Unknown Author' 
              },
              cover: latest.image_url || '',
              rating: latest.average_rating || 0,
              progress: {
                percentage: latest.progress_percentage || 0,
                currentPage: latest.current_page || 0,
                totalPages: latest.total_pages || 0,
                lastReadAt: latest.last_read_at || new Date().toISOString(),
              },
              timeLeftDisplay: `${Math.max(
                0,
                (latest.total_pages ?? 0) - (latest.current_page ?? 0)
              )} pages left`,
            },
          ]
        : [];

      // -----------------------------
      // Recently Viewed
      // -----------------------------
      dashboard.recentlyViewed = (history.history ?? []).slice(0, 8).map((book: any) => ({
        id: book.isbn || `book_${Date.now()}`,
        title: book.title || 'Untitled Book',
        author: {
          id: book.author || 'unknown-author',
          name: book.author || 'Unknown Author',
        },
        cover: book.image_url || '',
        rating: book.average_rating || 0,
        viewedAt: book.last_read_at || new Date().toISOString(),
      }));

      // -----------------------------
      // AI Recommendations - FIXED
      // -----------------------------
      dashboard.recommendations = [
        {
          id: "personalized",
          title: "Recommended For You",
          description: "Powered by your Hybrid AI Engine",
          featured: true,
          books: recResponse.recommendations.map((book) => ({
            id: book.isbn || `book_${Date.now()}`,
            title: book.title || 'Untitled Book',
            author: {
              id: book.authors || 'unknown-author',
              name: book.authors || 'Unknown Author',
            },
            cover: book.image_url || '',
            rating: book.average_rating || 0,
            score: book.recommendation_score || 0,
            reason: book.recommendation_reason || 'Recommended for you',
            algorithm: "hybrid" as const,
            recommendedAt: new Date().toISOString(),
          })),
        },
      ];

      dashboard.lastUpdated = new Date().toISOString();

      return dashboard;
    } catch (error) {
      console.error("Error fetching dashboard:", error);
      throw new Error("Failed to fetch dashboard");
    }
  }

  /**
   * Get dashboard statistics only.
   */
  async getStats(): Promise<DashboardStat[]> {
    try {
      return getDashboardStats();
    } catch (error) {
      console.error("Error fetching dashboard stats:", error);
      throw new Error("Failed to fetch dashboard stats");
    }
  }

  /**
   * Get a specific dashboard stat by title.
   */
  async getStat(title: string): Promise<DashboardStat | undefined> {
    if (!title || title.trim().length === 0) {
      throw new Error("Invalid stat title");
    }

    try {
      return getDashboardStat(title);
    } catch (error) {
      console.error(`Error fetching stat "${title}":`, error);
      throw new Error(`Failed to fetch stat "${title}"`);
    }
  }

  /**
   * Get the primary dashboard stat (first one).
   */
  async getPrimaryStat(): Promise<DashboardStat | undefined> {
    try {
      return getPrimaryStat();
    } catch (error) {
      console.error("Error fetching primary stat:", error);
      throw new Error("Failed to fetch primary stat");
    }
  }

  /**
   * Get dashboard stats with positive trends.
   */
  async getPositiveTrendStats(): Promise<DashboardStat[]> {
    try {
      return getPositiveTrendStats();
    } catch (error) {
      console.error("Error fetching positive trend stats:", error);
      throw new Error("Failed to fetch positive trend stats");
    }
  }

  /**
   * Get dashboard stats with negative trends.
   */
  async getNegativeTrendStats(): Promise<DashboardStat[]> {
    try {
      return getNegativeTrendStats();
    } catch (error) {
      console.error("Error fetching negative trend stats:", error);
      throw new Error("Failed to fetch negative trend stats");
    }
  }

  /**
   * Calculate overall progress percentage across all metrics.
   */
  async getOverallProgress(): Promise<number> {
    try {
      return getOverallProgress();
    } catch (error) {
      console.error("Error calculating overall progress:", error);
      throw new Error("Failed to calculate overall progress");
    }
  }

  /**
   * Format a stat value for display.
   */
  formatStatValue(stat: DashboardStat): string {
    return formatStatValue(stat);
  }

  /**
   * Get the color class for a stat trend.
   */
  getTrendColor(stat: DashboardStat): string {
    return getTrendColor(stat);
  }

  /**
   * Get the icon for a stat.
   */
  getStatIconName(stat: DashboardStat): string {
    return getStatIconName(stat);
  }

  /**
   * Check if dashboard has data.
   */
  async hasDashboardData(): Promise<boolean> {
    try {
      return hasDashboardData();
    } catch (error) {
      console.error("Error checking dashboard data:", error);
      return false;
    }
  }

  /**
   * Get dashboard summary.
   */
  async getSummary() {
    try {
      return getDashboardSummary();
    } catch (error) {
      console.error("Error fetching dashboard summary:", error);
      throw new Error("Failed to fetch dashboard summary");
    }
  }

  /**
   * Get recent activity.
   */
  async getRecentActivity() {
    try {
      return getRecentActivity();
    } catch (error) {
      console.error("Error fetching recent activity:", error);
      throw new Error("Failed to fetch recent activity");
    }
  }

  /**
   * Get dashboard status.
   */
  async getStatus() {
    try {
      return getDashboardStatus();
    } catch (error) {
      console.error("Error fetching dashboard status:", error);
      throw new Error("Failed to fetch dashboard status");
    }
  }

  /**
   * Refresh dashboard data.
   */
  async refreshDashboard(): Promise<DashboardData> {
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const data = getDashboardData();
      data.lastUpdated = new Date().toISOString();
      
      return data;
    } catch (error) {
      console.error("Error refreshing dashboard:", error);
      throw new Error("Failed to refresh dashboard");
    }
  }

  /**
   * Get dashboard data with formatted stats for UI display.
   */
  async getFormattedDashboard() {
    try {
      const dashboard = await this.getDashboard();
      const stats = dashboard.stats.map(stat => ({
        ...stat,
        formattedValue: this.formatStatValue(stat),
        trendColor: this.getTrendColor(stat),
        iconName: this.getStatIconName(stat),
      }));

      return {
        ...dashboard,
        stats,
        summary: await this.getSummary(),
        activity: await this.getRecentActivity(),
        status: await this.getStatus(),
      };
    } catch (error) {
      console.error("Error fetching formatted dashboard:", error);
      throw new Error("Failed to fetch formatted dashboard");
    }
  }
}

// ============================================================
// 📦 Export Singleton Instance
// ============================================================

export const dashboardService = new DashboardService();