// lib/types/common.ts

/**
 * ================================================================
 * 🔧 Common Types
 * ================================================================
 *
 * These are shared types used across the entire application.
 * They provide consistent type definitions for common patterns.
 * ================================================================
 */

// ============================================================
// 📦 Basic Types
// ============================================================

/**
 * Represents a unique identifier (number or string UUID).
 */
export type ID = number | string;

/**
 * Represents a timestamp as an ISO string.
 */
export type Timestamp = string;

/**
 * Represents a value that can be null or undefined.
 */
export type Maybe<T> = T | null | undefined;

/**
 * Represents an ISO date string.
 */
export type ISODateString = string;

// ============================================================
// 📄 Pagination
// ============================================================

/**
 * Represents a paginated response.
 */
export interface PaginatedResponse<T> {
  /** List of items for the current page */
  items: T[];
  
  /** Total number of items across all pages */
  total: number;
  
  /** Current page number (1-indexed) */
  page: number;
  
  /** Number of items per page */
  limit: number;
  
  /** Total number of pages */
  totalPages: number;
}

/**
 * Pagination parameters for API requests.
 */
export interface PaginationParams {
  /** Page number (1-indexed) */
  page?: number;
  
  /** Number of items per page */
  limit?: number;
  
  /** Field to sort by */
  sortBy?: string;
  
  /** Sort direction */
  sortOrder?: "asc" | "desc";
}

// ============================================================
// 🔍 Filtering
// ============================================================

/**
 * Represents a sort direction.
 */
export type SortDirection = "asc" | "desc";

/**
 * Represents a filter operator.
 */
export type FilterOperator = 
  | "eq"    // equals
  | "neq"   // not equals
  | "gt"    // greater than
  | "gte"   // greater than or equal
  | "lt"    // less than
  | "lte"   // less than or equal
  | "contains"
  | "startsWith"
  | "endsWith";

/**
 * Represents a filter condition.
 */
export interface FilterCondition {
  /** The field to filter on */
  field: string;
  
  /** The operator to use */
  operator: FilterOperator;
  
  /** The value to compare against */
  value: unknown;
}

// ============================================================
// 📊 API Responses
// ============================================================

/**
 * Standard API response wrapper.
 */
export interface ApiResponse<T> {
  /** Whether the request was successful */
  success: boolean;
  
  /** The response data (if successful) */
  data?: T;
  
  /** Error message (if failed) */
  error?: string;
  
  /** HTTP status code */
  statusCode?: number;
  
  /** Timestamp of the response */
  timestamp?: Timestamp;
}

/**
 * Standard API error response.
 */
export interface ApiError {
  /** Error message */
  message: string;
  
  /** Error code */
  code?: string;
  
  /** Additional error details */
  details?: Record<string, unknown>;
}

// ============================================================
// 🎯 Utility Types
// ============================================================

/**
 * Makes all properties optional recursively.
 */
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

/**
 * Makes all properties required recursively.
 */
export type DeepRequired<T> = {
  [P in keyof T]-?: T[P] extends object ? DeepRequired<T[P]> : T[P];
};

/**
 * Picks a subset of properties from a type.
 */
export type PickPartial<T, K extends keyof T> = Pick<T, K> & Partial<Omit<T, K>>;

/**
 * Nullable version of a type.
 */
export type Nullable<T> = T | null;

/**
 * Optional version of a type.
 */
export type Optional<T> = T | undefined;

// ============================================================
// 📅 Date Helpers
// ============================================================

/**
 * Format a timestamp to a readable date string.
 */
export function formatDate(timestamp?: Timestamp): string {
  if (!timestamp) return "N/A";
  try {
    const date = new Date(timestamp);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return String(timestamp);
  }
}

/**
 * Format a timestamp to a readable date and time string.
 */
export function formatDateTime(timestamp?: Timestamp): string {
  if (!timestamp) return "N/A";
  try {
    const date = new Date(timestamp);
    return date.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return String(timestamp);
  }
}

/**
 * Get the time ago string from a timestamp.
 */
export function timeAgo(timestamp?: Timestamp): string {
  if (!timestamp) return "N/A";
  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 30) return `${Math.floor(days / 30)} months ago`;
    if (days > 7) return `${Math.floor(days / 7)} weeks ago`;
    if (days > 0) return `${days} days ago`;
    if (hours > 0) return `${hours} hours ago`;
    if (minutes > 0) return `${minutes} minutes ago`;
    return "Just now";
  } catch {
    return String(timestamp);
  }
}

