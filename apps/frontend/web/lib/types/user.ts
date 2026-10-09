/**
 * ================================================================
 * 👤 User Types
 * ================================================================
 *
 * These types define the user-related data structures for the frontend.
 * They handle:
 * - User profiles
 * - User preferences
 * - Reading statistics
 * - Account settings
 * ================================================================
 */

import type { ID } from "./common";

// ============================================================
// 👤 User
// ============================================================

/**
 * Basic user information.
 */
export interface User {
  /** Unique user identifier */
  id: ID;

  /** Unique username */
  username: string;

  /** User's email address */
  email: string;

  /** User's full display name */
  fullName: string;

  /** URL to user's profile avatar */
  avatar?: string;

  /** Account creation timestamp */
  createdAt?: string;

  /** Account last updated timestamp */
  updatedAt?: string;  // ✅ Add this

  /** Last login timestamp */
  lastLogin?: string;

  /** Whether the user's email is verified */
  isEmailVerified?: boolean;

  /** Whether the user is currently active */
  isActive?: boolean;

  /** User's role */
  role?: "user" | "admin" | "superuser";

  /** Whether the user is verified (for auth purposes) */
  isVerified?: boolean;

  /** Whether the user is authenticated (for CurrentUser) */
  isAuthenticated?: boolean;
}

// ============================================================
// 🎯 User Preferences
// ============================================================

/**
 * User's reading and content preferences.
 */
export interface UserPreferences {
  /** Favorite genres */
  favoriteGenres?: string[];

  /** Preferred languages (ISO codes) */
  preferredLanguages?: string[];

  /** Favorite authors */
  favoriteAuthors?: string[];

  /** Whether to show mature content */
  allowMatureContent?: boolean;

  /** Preferred reading format */
  preferredFormat?: "ebook" | "paperback" | "audiobook";

  /** Notification preferences */
  notifications?: {
    email?: boolean;
    push?: boolean;
    inApp?: boolean;
  };
}

// ============================================================
// 📊 User Statistics
// ============================================================

/**
 * User's reading statistics and achievements.
 */
export interface UserStats {
  /** Total books completed */
  booksCompleted?: number;

  /** Books currently in progress */
  booksInProgress?: number;

  /** Books saved to library */
  booksSaved?: number;

  /** Total pages read */
  totalPagesRead?: number;

  /** Current reading streak in days */
  currentReadingStreak?: number;

  /** Longest reading streak achieved */
  longestReadingStreak?: number;

  /** Total reading time in minutes */
  totalReadingTime?: number;

  /** Average rating given */
  averageRating?: number;

  /** Books abandoned (did not finish) */
  booksAbandoned?: number;

  /** Most active reading month */
  mostActiveMonth?: string;
}

// ============================================================
// 🔒 Account Settings
// ============================================================

/**
 * User's account and privacy settings.
 */
export interface UserSettings {
  /** Whether the profile is public */
  isProfilePublic?: boolean;

  /** Whether to show reading activity */
  showReadingActivity?: boolean;

  /** Theme preference */
  theme?: "light" | "dark" | "system";

  /** Default view mode */
  defaultView?: "grid" | "list" | "compact";
}

// ============================================================
// 👤 Current User
// ============================================================

/**
 * Currently authenticated user.
 * Extends the base User with preferences, stats, and settings.
 */
export interface CurrentUser extends User {
  /** User preferences */
  preferences?: UserPreferences;

  /** Reading statistics */
  stats?: UserStats;

  /** Account settings */
  settings?: UserSettings;
}

// ============================================================
// 📝 User Creation
// ============================================================

/**
 * Data required to create a new user.
 */
export interface CreateUserData {
  username: string;
  email: string;
  password: string;
  fullName?: string;
}

/**
 * Data required to update a user.
 */
export interface UpdateUserData {
  username?: string;
  email?: string;
  fullName?: string;
  avatar?: string;
  preferences?: Partial<UserPreferences>;
  settings?: Partial<UserSettings>;
}

// ============================================================
// 🔄 Helper Functions
// ============================================================

/**
 * Get the user's display name with fallback.
 */
export function getUserDisplayName(user: CurrentUser): string {
  return user.fullName || user.username || "User";
}

/**
 * Get the user's initials for avatar fallback.
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
 */
export function hasReadingStreak(user: CurrentUser): boolean {
  return (user.stats?.currentReadingStreak || 0) > 0;
}

/**
 * Get the user's reading streak message.
 */
export function getStreakMessage(user: CurrentUser): string {
  const streak = user.stats?.currentReadingStreak || 0;
  if (streak === 0) return "Start a reading streak today! 🔥";
  if (streak < 7) return `${streak} day${streak > 1 ? "s" : ""} streak! Keep going! 📚`;
  if (streak < 30) return `${streak} days! Amazing consistency! 🎯`;
  return `${streak} days! Reading master! 🏆`;
}

/**
 * Get the user's reading level based on books completed.
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
 */
export function getReadingLevelLabel(user: CurrentUser): string {
  const labels = {
    beginner: "📖 Beginner Reader",
    intermediate: "📚 Intermediate Reader",
    advanced: "🏆 Advanced Reader",
    expert: "👑 Expert Reader",
  };
  return labels[getReadingLevel(user)] || "📖 Beginner Reader";
}

/**
 * Get the user's total reading time in hours.
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
 */
export function getCompletionRate(user: CurrentUser): number {
  const completed = user.stats?.booksCompleted || 0;
  const abandoned = user.stats?.booksAbandoned || 0;
  const total = completed + abandoned;
  if (total === 0) return 0;
  return Math.round((completed / total) * 100);
}

/**
 * Get the user's profile completion percentage.
 */
export function getProfileCompletion(user: CurrentUser): number {
  let fields = 0;
  const total = 6;
  
  if (user.id) fields++;
  if (user.username) fields++;
  if (user.email) fields++;
  if (user.fullName) fields++;
  if (user.avatar) fields++;
  if (user.preferences?.favoriteGenres?.length) fields++;
  
  return Math.round((fields / total) * 100);
}