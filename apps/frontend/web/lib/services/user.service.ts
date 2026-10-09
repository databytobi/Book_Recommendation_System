/**
 * ================================================================
 * 👤 User Service
 * ================================================================
 *
 * Handles all user-related operations including:
 * - Getting current user
 * - Updating user profile
 * - Updating user preferences
 * - Updating user settings
 * - Getting user statistics
 *
 * Currently backed by mock data.
 * Will later communicate with the backend API.
 * ================================================================
 */

// Import directly from the file to avoid any export issues
import { currentUser, getCurrentUser } from "@/lib/mock/users";
import type { CurrentUser, UserPreferences, UserSettings, UpdateUserData } from "@/lib/types/user";

// ============================================================
// 👤 User Service Class
// ============================================================

class UserService {
  /**
   * Returns the authenticated user.
   */
  async getCurrentUser(): Promise<CurrentUser> {
    try {
      return getCurrentUser();
    } catch (error) {
      console.error("Error fetching current user:", error);
      throw new Error("Failed to fetch current user");
    }
  }

  /**
   * Update the current user's profile.
   */
  async updateProfile(data: Partial<UpdateUserData>): Promise<CurrentUser> {
    if (!data || Object.keys(data).length === 0) {
      throw new Error("No update data provided");
    }

    try {
      const user: CurrentUser = JSON.parse(JSON.stringify(currentUser));
      
      if (data.fullName !== undefined) {
        user.fullName = data.fullName;
      }
      if (data.username !== undefined) {
        user.username = data.username;
      }
      if (data.email !== undefined) {
        user.email = data.email;
      }
      if (data.avatar !== undefined) {
        user.avatar = data.avatar;
      }

      return user;
    } catch (error) {
      console.error("Error updating user profile:", error);
      throw new Error("Failed to update user profile");
    }
  }

  /**
   * Update the current user's preferences.
   */
  async updatePreferences(preferences: Partial<UserPreferences>): Promise<CurrentUser> {
    if (!preferences || Object.keys(preferences).length === 0) {
      throw new Error("No preferences provided");
    }

    try {
      const user: CurrentUser = JSON.parse(JSON.stringify(currentUser));
      
      if (!user.preferences) {
        user.preferences = {};
      }

      // Use type assertion to work around TypeScript cache issue
      const prefs = preferences as any;
      
      if (prefs.favoriteGenres !== undefined) {
        user.preferences.favoriteGenres = prefs.favoriteGenres;
      }
      if (prefs.preferredLanguages !== undefined) {
        user.preferences.preferredLanguages = prefs.preferredLanguages;
      }
      if (prefs.favoriteAuthors !== undefined) {
        user.preferences.favoriteAuthors = prefs.favoriteAuthors;
      }
      if (prefs.allowMatureContent !== undefined) {
        user.preferences.allowMatureContent = prefs.allowMatureContent;
      }
      if (prefs.preferredFormat !== undefined) {
        user.preferences.preferredFormat = prefs.preferredFormat;
      }
      if (prefs.notifications !== undefined) {
        user.preferences.notifications = {
          ...user.preferences.notifications,
          ...prefs.notifications,
        };
      }

      return user;
    } catch (error) {
      console.error("Error updating user preferences:", error);
      throw new Error("Failed to update user preferences");
    }
  }

  /**
   * Update the current user's settings.
   */
  async updateSettings(settings: Partial<UserSettings>): Promise<CurrentUser> {
    if (!settings || Object.keys(settings).length === 0) {
      throw new Error("No settings provided");
    }

    try {
      const user: CurrentUser = JSON.parse(JSON.stringify(currentUser));
      
      if (!user.settings) {
        user.settings = {};
      }

      if (settings.theme !== undefined) {
        user.settings.theme = settings.theme;
      }
      if (settings.isProfilePublic !== undefined) {
        user.settings.isProfilePublic = settings.isProfilePublic;
      }
      if (settings.showReadingActivity !== undefined) {
        user.settings.showReadingActivity = settings.showReadingActivity;
      }
      if (settings.defaultView !== undefined) {
        user.settings.defaultView = settings.defaultView;
      }

      return user;
    } catch (error) {
      console.error("Error updating user settings:", error);
      throw new Error("Failed to update user settings");
    }
  }

  /**
   * Get user statistics.
   */
  async getUserStats() {
    try {
      const user = await this.getCurrentUser();
      
      return {
        booksCompleted: user.stats?.booksCompleted || 0,
        booksInProgress: user.stats?.booksInProgress || 0,
        booksSaved: user.stats?.booksSaved || 0,
        totalPagesRead: user.stats?.totalPagesRead || 0,
        currentReadingStreak: user.stats?.currentReadingStreak || 0,
        longestReadingStreak: user.stats?.longestReadingStreak || 0,
        totalReadingTime: user.stats?.totalReadingTime || 0,
        averageRating: user.stats?.averageRating || 0,
        booksAbandoned: user.stats?.booksAbandoned || 0,
        mostActiveMonth: user.stats?.mostActiveMonth || "N/A",
      };
    } catch (error) {
      console.error("Error fetching user stats:", error);
      throw new Error("Failed to fetch user stats");
    }
  }

  /**
   * Update user avatar.
   */
  async updateAvatar(avatarUrl: string): Promise<CurrentUser> {
    if (!avatarUrl || avatarUrl.trim().length === 0) {
      throw new Error("Invalid avatar URL");
    }

    try {
      const user: CurrentUser = JSON.parse(JSON.stringify(currentUser));
      user.avatar = avatarUrl;
      return user;
    } catch (error) {
      console.error("Error updating user avatar:", error);
      throw new Error("Failed to update user avatar");
    }
  }

  /**
   * Get the user's display name.
   */
  async getDisplayName(): Promise<string> {
    try {
      const user = await this.getCurrentUser();
      return user.fullName || user.username || "User";
    } catch (error) {
      console.error("Error fetching display name:", error);
      return "User";
    }
  }

  /**
   * Get the user's initials.
   */
  async getUserInitials(): Promise<string> {
    try {
      const name = await this.getDisplayName();
      const parts = name.split(" ");
      if (parts.length >= 2) {
        return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
      }
      return name.slice(0, 2).toUpperCase();
    } catch (error) {
      console.error("Error fetching user initials:", error);
      return "U";
    }
  }

  /**
   * Check if the user has a reading streak.
   */
  async hasReadingStreak(): Promise<boolean> {
    try {
      const stats = await this.getUserStats();
      return (stats.currentReadingStreak || 0) > 0;
    } catch (error) {
      console.error("Error checking reading streak:", error);
      return false;
    }
  }

  /**
   * Get the user's reading streak message.
   */
  async getStreakMessage(): Promise<string> {
    try {
      const stats = await this.getUserStats();
      const streak = stats.currentReadingStreak || 0;
      
      if (streak === 0) return "Start a reading streak today! 🔥";
      if (streak < 7) return `${streak} day${streak > 1 ? "s" : ""} streak! Keep going! 📚`;
      if (streak < 30) return `${streak} days! Amazing consistency! 🎯`;
      return `${streak} days! Reading master! 🏆`;
    } catch (error) {
      console.error("Error fetching streak message:", error);
      return "Start a reading streak today! 🔥";
    }
  }

  /**
   * Get the user's reading level.
   */
  async getReadingLevel(): Promise<"beginner" | "intermediate" | "advanced" | "expert"> {
    try {
      const stats = await this.getUserStats();
      const books = stats.booksCompleted || 0;
      
      if (books === 0) return "beginner";
      if (books < 10) return "beginner";
      if (books < 30) return "intermediate";
      if (books < 60) return "advanced";
      return "expert";
    } catch (error) {
      console.error("Error fetching reading level:", error);
      return "beginner";
    }
  }

  /**
   * Get the user's reading level label.
   */
  async getReadingLevelLabel(): Promise<string> {
    try {
      const level = await this.getReadingLevel();
      const labels = {
        beginner: "📖 Beginner Reader",
        intermediate: "📚 Intermediate Reader",
        advanced: "🏆 Advanced Reader",
        expert: "👑 Expert Reader",
      };
      return labels[level] || "📖 Beginner Reader";
    } catch (error) {
      console.error("Error fetching reading level label:", error);
      return "📖 Beginner Reader";
    }
  }

  /**
   * Get user profile completion percentage.
   */
  async getProfileCompletion(): Promise<number> {
    try {
      const user = await this.getCurrentUser();
      let fields = 0;
      const total = 6;
      
      if (user.id) fields++;
      if (user.username) fields++;
      if (user.email) fields++;
      if (user.fullName) fields++;
      if (user.avatar) fields++;
      if (user.preferences?.favoriteGenres?.length) fields++;
      
      return Math.round((fields / total) * 100);
    } catch (error) {
      console.error("Error calculating profile completion:", error);
      return 0;
    }
  }
}

// ============================================================
// 📦 Export Singleton Instance
// ============================================================

export const userService = new UserService();