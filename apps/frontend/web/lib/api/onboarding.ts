// apps/frontend/web/lib/api/onboarding.ts

import { apiClient } from "./client";

/* -------------------------------------------------------------------------- */
/* Types                                                                      */
/* -------------------------------------------------------------------------- */

export type OnboardingStep =
  | "welcome"
  | "genres"
  | "authors"
  | "books"
  | "reading_goal"
  | "complete";

export type ReadingGoal =
  | "light"
  | "moderate"
  | "avid"
  | "intense";

export type ReadingStyle =
  | "quick"
  | "balanced"
  | "deep"
  | "explorer";

export type Language =
  | "en"
  | "es"
  | "fr"
  | "de"
  | "it"
  | "pt"
  | "nl"
  | "ru"
  | "ja"
  | "zh"
  | "ar"
  | "hi";

export type Theme =
  | "dark"
  | "light"
  | "system";

/* -------------------------------------------------------------------------- */
/* Request Types                                                              */
/* -------------------------------------------------------------------------- */

export interface OnboardingRequest {
  favorite_authors: string[];
  favorite_books: string[];
  preferred_genres: string[];

  reading_goal?: ReadingGoal | null;
  reading_style?: ReadingStyle | null;

  preferred_language?: Language | null;

  recommendation_count?: number | null;

  theme?: Theme | null;

  metadata?: Record<string, unknown> | null;
}

export interface OnboardingStepUpdateRequest {
  step: OnboardingStep;

  data?: Record<string, unknown> | null;
}

/* -------------------------------------------------------------------------- */
/* Response Types                                                             */
/* -------------------------------------------------------------------------- */

export interface OnboardingPreferenceSummary {
  total_genres: number;
  total_authors: number;
  total_books: number;

  reading_goal: string;
  reading_goal_books: number;

  language: string;
  theme: string;

  top_genres?: string[];
  top_authors?: string[];
  top_books?: string[];
}

export interface OnboardingProgressResponse {
  user_id: number;

  current_step: string;

  completed_steps: string[];

  progress_percentage: number;

  is_complete: boolean;

  next_step?: string | null;

  total_steps: number;
}

export interface OnboardingResponse {
  success: boolean;

  message: string;

  completed_steps?: string[];

  recommendations_ready?: boolean;

  preference_summary?: Record<string, unknown> | null;

  next_step?: string | null;

  progress_percentage?: number | null;

  timestamp?: string | null;
}

export interface SkipOnboardingResponse {
  [key: string]: unknown;
}

export interface ResetOnboardingResponse {
  [key: string]: unknown;
}

export interface OnboardingHealthResponse {
  [key: string]: unknown;
}

/* -------------------------------------------------------------------------- */
/* API                                                                       */
/* -------------------------------------------------------------------------- */

/**
 * Complete the user's onboarding.
 *
 * Sends all onboarding preferences to the backend.
 */
export async function completeOnboarding(
  data: OnboardingRequest
): Promise<OnboardingResponse> {
  return apiClient.post<OnboardingResponse>(
    "/onboarding/onboarding/complete",
    data
  );
}

/**
 * Save partial onboarding progress.
 *
 * This is useful when the user moves between onboarding steps
 * and we want to persist their current selections.
 */
export async function saveOnboardingProgress(
  data: OnboardingRequest
): Promise<OnboardingResponse> {
  return apiClient.post<OnboardingResponse>(
    "/onboarding/onboarding/progress",
    data
  );
}

/**
 * Get the current onboarding progress.
 */
export async function getOnboardingStatus(): Promise<OnboardingProgressResponse> {
  return apiClient.get<OnboardingProgressResponse>(
    "/onboarding/onboarding/status"
  );
}

/**
 * Skip onboarding.
 */
export async function skipOnboarding(): Promise<SkipOnboardingResponse> {
  return apiClient.post<SkipOnboardingResponse>(
    "/onboarding/onboarding/skip"
  );
}

/**
 * Mark an onboarding step as completed.
 */
export async function completeOnboardingStep(
  step: OnboardingStep,
  data?: Record<string, unknown> | null
): Promise<OnboardingProgressResponse> {
  const payload: OnboardingStepUpdateRequest = {
    step,
    data,
  };

  return apiClient.post<OnboardingProgressResponse>(
    `/onboarding/onboarding/step/${encodeURIComponent(step)}`,
    payload
  );
}

/**
 * Get a summary of the user's onboarding preferences.
 */
export async function getOnboardingPreferences(): Promise<OnboardingPreferenceSummary> {
  return apiClient.get<OnboardingPreferenceSummary>(
    "/onboarding/onboarding/preferences"
  );
}

/**
 * Reset onboarding progress.
 */
export async function resetOnboarding(): Promise<ResetOnboardingResponse> {
  return apiClient.post<ResetOnboardingResponse>(
    "/onboarding/onboarding/reset"
  );
}

/**
 * Check whether the onboarding service is healthy.
 */
export async function getOnboardingHealth(): Promise<OnboardingHealthResponse> {
  return apiClient.get<OnboardingHealthResponse>(
    "/onboarding/onboarding/health"
  );
}