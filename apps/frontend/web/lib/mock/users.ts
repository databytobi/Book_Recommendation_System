// apps/frontend/web/lib/mock/users.ts

/**
 * ================================================================
 * 👤 User Mock Data
 * ================================================================
 *
 * This file contains mock user data for development and testing.
 * It represents a fully authenticated user with:
 * - Basic account information
 * - Reading preferences
 * - Reading statistics
 * - Account settings
 *
 * IMPORTANT: This is mock data and should be replaced with
 * real API data in production.
 * ================================================================
 */

import type { CurrentUser } from "@/lib/types";
import { DEFAULT_AVATAR } from "@/lib/constants/mock";

// ============================================================
// 👤 Mock User
// ============================================================

/**
 * Mock authenticated user.
 * 
 * Represents a fully authenticated user with:
 * - Basic account information
 * - Reading preferences
 * - Reading statistics
 * - Account settings
 * 
 * Used for development and testing when the backend is not available.
 */
export const currentUser: CurrentUser = {
  // ============================================================
  // 📋 Basic Account Information
  // ============================================================

  /** Unique user identifier */
  id: 1,

  /** Unique username */
  username: "brunotalley",

  /** User's email address (verified) */
  email: "bruno@example.com",

  /** User's full display name */
  fullName: "Bruno Talley",

  /** URL to user's profile avatar (fallback to default) */
  avatar: DEFAULT_AVATAR,

  /** Account creation timestamp */
  createdAt: "2024-01-15T10:30:00Z",

  /** Last login timestamp */
  lastLogin: "2026-07-20T14:30:00Z",

  /** Whether the user's email is verified */
  isEmailVerified: true,

  /** Whether the user is currently active */
  isActive: true,

  /** User's role (determines permissions) */
  role: "user",

  // ============================================================
  // 🎯 User Preferences
  // ============================================================

  /**
   * User's reading and content preferences.
   * Used for personalizing recommendations and content.
   */
  preferences: {
    /** Favorite genres the user enjoys reading */
    favoriteGenres: [
      "Technology",
      "Fantasy",
      "Science Fiction",
      "Business",
    ],

    /** Preferred languages (ISO codes) */
    preferredLanguages: ["en"],

    /** Favorite authors the user follows or enjoys */
    favoriteAuthors: [
      "James Clear",
      "Cal Newport",
      "Frank Herbert",
    ],

    /** Whether to show mature content */
    allowMatureContent: false,

    /** Preferred reading format */
    preferredFormat: "ebook",

    /** Notification preferences */
    notifications: {
      email: true,
      push: true,
      inApp: true,
    },
  },

  // ============================================================
  // 📊 Reading Statistics
  // ============================================================

  /**
   * User's reading statistics and achievements.
   * Used for the dashboard and profile display.
   */
  stats: {
    /** Total books completed by the user */
    booksCompleted: 48,

    /** Books currently in progress */
    booksInProgress: 3,

    /** Books saved to the user's library */
    booksSaved: 17,

    /** Total pages read across all books */
    totalPagesRead: 16872,

    /** Current reading streak in days */
    currentReadingStreak: 14,

    /** Longest reading streak achieved */
    longestReadingStreak: 45,

    /** Total reading time in minutes */
    totalReadingTime: 8436,

    /** Average rating given by the user */
    averageRating: 4.3,

    /** Total books abandoned (did not finish) */
    booksAbandoned: 5,

    /** Most active reading month */
    mostActiveMonth: "January",
  },

  // ============================================================
  // 🔒 Account Settings
  // ============================================================

  /**
   * User's account and privacy settings.
   */
  settings: {
    /** Whether the profile is public */
    isProfilePublic: true,

    /** Whether to show reading activity */
    showReadingActivity: true,

    /** Theme preference */
    theme: "dark",

    /** Default view mode */
    defaultView: "grid",
  },
};

// ============================================================
// 🔄 Helper Functions
// ============================================================

/**
 * Get the current user.
 * Returns a copy of the mock user data.
 * 
 * @returns CurrentUser - The current user
 * 
 * @example
 * ```ts
 * const user = getCurrentUser();
 * console.log(user.fullName); // "Bruno Talley"
 * ```
 */
export function getCurrentUser(): CurrentUser {
  // Return a deep copy to prevent accidental mutations
  return JSON.parse(JSON.stringify(currentUser));
}

/**
 * Get the user's display name with fallback.
 * 
 * @param user - The user object
 * @returns string - User's display name
 * 
 * @example
 * ```ts
 * const name = getUserDisplayName(user);
 * console.log(name); // "Bruno Talley"
 * ```
 */
export function getUserDisplayName(user: CurrentUser): string {
  return user.fullName || user.username || "User";
}

/**
 * Get the user's initials for avatar fallback.
 * 
 * @param user - The user object
 * @returns string - User's initials
 * 
 * @example
 * ```ts
 * const initials = getUserInitials(user);
 * console.log(initials); // "BT"
 * ```
 */
export function getUserInitials(user: CurrentUser): string {
  const name = getUserDisplayName(user);
  const parts = name.split(" ");
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
}

/**
 * Check if the user has a reading streak.
 * 
 * @param user - The user object
 * @returns boolean - True if the user has a reading streak
 * 
 * @example
 * ```ts
 * const hasStreak = hasReadingStreak(user);
 * console.log(hasStreak); // true
 * ```
 */
export function hasReadingStreak(user: CurrentUser): boolean {
  return (user.stats?.currentReadingStreak || 0) > 0;
}

/**
 * Get the user's reading streak message.
 * 
 * @param user - The user object
 * @returns string - Streak message
 * 
 * @example
 * ```ts
 * const message = getStreakMessage(user);
 * console.log(message); // "14 days! Amazing consistency! 🎯"
 * ```
 */
export function getStreakMessage(user: CurrentUser): string {
  const streak = user.stats?.currentReadingStreak || 0;
  if (streak === 0) return "Start a reading streak today! 🔥";
  if (streak < 7) return `${streak} day${streak > 1 ? "s" : ""} streak! Keep going! 📚`;
  if (streak < 30) return `${streak} days! Amazing consistency! 🎯`;
  return `${streak} days! Reading master! 🏆`;
}

/**
 * Check if the user has completed any books.
 * 
 * @param user - The user object
 * @returns boolean - True if the user has completed books
 * 
 * @example
 * ```ts
 * const hasCompleted = hasCompletedBooks(user);
 * console.log(hasCompleted); // true
 * ```
 */
export function hasCompletedBooks(user: CurrentUser): boolean {
  return (user.stats?.booksCompleted || 0) > 0;
}

/**
 * Get the user's reading level based on books completed.
 * 
 * @param user - The user object
 * @returns string - Reading level
 * 
 * @example
 * ```ts
 * const level = getReadingLevel(user);
 * console.log(level); // "advanced"
 * ```
 */
export function getReadingLevel(user: CurrentUser): "beginner" | "intermediate" | "advanced" | "expert" {
  const books = user.stats?.booksCompleted || 0;
  if (books === 0) return "beginner";
  if (books < 10) return "beginner";
  if (books < 30) return "intermediate";
  if (books < 60) return "advanced";
  return "expert";
}

/**
 * Get the user's reading level label.
 * 
 * @param user - The user object
 * @returns string - Reading level label
 * 
 * @example
 * ```ts
 * const label = getReadingLevelLabel(user);
 * console.log(label); // "🏆 Advanced Reader"
 * ```
 */
export function getReadingLevelLabel(user: CurrentUser): string {
  const level = getReadingLevel(user);
  const labels = {
    beginner: "📖 Beginner Reader",
    intermediate: "📚 Intermediate Reader",
    advanced: "🏆 Advanced Reader",
    expert: "👑 Expert Reader",
  };
  return labels[level] || "📖 Beginner Reader";
}

/**
 * Get the user's total reading time in hours.
 * 
 * @param user - The user object
 * @returns string - Formatted reading time
 * 
 * @example
 * ```ts
 * const hours = getTotalReadingHours(user);
 * console.log(hours); // "140h 36m"
 * ```
 */
export function getTotalReadingHours(user: CurrentUser): string {
  const minutes = user.stats?.totalReadingTime || 0;
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  if (hours === 0) return `${remainingMinutes}m`;
  if (remainingMinutes === 0) return `${hours}h`;
  return `${hours}h ${remainingMinutes}m`;
}

/**
 * Get the user's reading completion rate.
 * 
 * @param user - The user object
 * @returns number - Completion rate percentage
 * 
 * @example
 * ```ts
 * const rate = getCompletionRate(user);
 * console.log(rate); // 90
 * ```
 */
export function getCompletionRate(user: CurrentUser): number {
  const completed = user.stats?.booksCompleted || 0;
  const abandoned = user.stats?.booksAbandoned || 0;
  const total = completed + abandoned;
  if (total === 0) return 0;
  return Math.round((completed / total) * 100);
}

/**
 * Check if the user has a specific genre preference.
 * 
 * @param user - The user object
 * @param genre - The genre to check
 * @returns boolean - True if the user prefers the genre
 * 
 * @example
 * ```ts
 * const prefers = hasGenrePreference(user, "Fantasy");
 * console.log(prefers); // true
 * ```
 */
export function hasGenrePreference(user: CurrentUser, genre: string): boolean {
  return user.preferences?.favoriteGenres?.some(g => 
    g.toLowerCase() === genre.toLowerCase()
  ) || false;
}

/**
 * Check if the user has a specific author preference.
 * 
 * @param user - The user object
 * @param author - The author to check
 * @returns boolean - True if the user prefers the author
 * 
 * @example
 * ```ts
 * const prefers = hasAuthorPreference(user, "James Clear");
 * console.log(prefers); // true
 * ```
 */
export function hasAuthorPreference(user: CurrentUser, author: string): boolean {
  return user.preferences?.favoriteAuthors?.some(a => 
    a.toLowerCase() === author.toLowerCase()
  ) || false;
}

/**
 * Get the user's favorite genres as a string.
 * 
 * @param user - The user object
 * @returns string - Comma-separated genres
 * 
 * @example
 * ```ts
 * const genres = getFavoriteGenresString(user);
 * console.log(genres); // "Technology, Fantasy, Science Fiction, Business"
 * ```
 */
export function getFavoriteGenresString(user: CurrentUser): string {
  const genres = user.preferences?.favoriteGenres || [];
  if (genres.length === 0) return "No favorite genres set";
  return genres.join(", ");
}

/**
 * Get the user's favorite authors as a string.
 * 
 * @param user - The user object
 * @returns string - Comma-separated authors
 * 
 * @example
 * ```ts
 * const authors = getFavoriteAuthorsString(user);
 * console.log(authors); // "James Clear, Cal Newport, Frank Herbert"
 * ```
 */
export function getFavoriteAuthorsString(user: CurrentUser): string {
  const authors = user.preferences?.favoriteAuthors || [];
  if (authors.length === 0) return "No favorite authors set";
  return authors.join(", ");
}

/**
 * Get the user's profile completion percentage.
 * 
 * @param user - The user object
 * @returns number - Profile completion percentage
 * 
 * @example
 * ```ts
 * const completion = getProfileCompletion(user);
 * console.log(completion); // 100
 * ```
 */
export function getProfileCompletion(user: CurrentUser): number {
  let fields = 0;
  const total = 6; // id, username, email, fullName, avatar, preferences
  
  if (user.id) fields++;
  if (user.username) fields++;
  if (user.email) fields++;
  if (user.fullName) fields++;
  if (user.avatar) fields++;
  if (user.preferences?.favoriteGenres?.length) fields++;
  
  return Math.round((fields / total) * 100);
}

/**
 * Format user's join date.
 * 
 * @param user - The user object
 * @returns string - Formatted join date
 * 
 * @example
 * ```ts
 * const date = getJoinDateDisplay(user);
 * console.log(date); // "January 15, 2024"
 * ```
 */
export function getJoinDateDisplay(user: CurrentUser): string {
  if (!user.createdAt) return "Unknown";
  try {
    const date = new Date(user.createdAt);
    return date.toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return user.createdAt;
  }
}

/**
 * Get the user's status color.
 * 
 * @param user - The user object
 * @returns string - CSS color class
 * 
 * @example
 * ```ts
 * const color = getUserStatusColor(user);
 * console.log(color); // "text-emerald-500"
 * ```
 */
export function getUserStatusColor(user: CurrentUser): string {
  if (!user.isActive) return "text-muted-foreground";
  if (user.isEmailVerified) return "text-emerald-500";
  return "text-amber-500";
}

/**
 * Get the user's status label.
 * 
 * @param user - The user object
 * @returns string - Status label
 * 
 * @example
 * ```ts
 * const label = getUserStatusLabel(user);
 * console.log(label); // "Verified"
 * ```
 */
export function getUserStatusLabel(user: CurrentUser): string {
  if (!user.isActive) return "Inactive";
  if (user.isEmailVerified) return "Verified";
  return "Unverified";
}