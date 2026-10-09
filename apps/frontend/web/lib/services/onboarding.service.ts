// apps/frontend/web/lib/services/onboarding.service.ts

import { apiClient } from "@/lib/api/client";

export interface PreferenceOption {
  id: number;
  label: string;
  description?: string;
}

export interface Author {
  id: number;
  name: string;
  image_url?: string | null;
  books_count?: number;
}

export interface Book {
  id: number;
  title: string;
  cover?: string | null;
  author?: {
    id: number;
    name: string;
  };
}

export interface ReadingStyle {
  id: number;
  title: string;
  description: string;
}

// ------------------------------------------------
// Types
// ------------------------------------------------

export interface CompleteOnboardingRequest {
  preferred_genres: string[];
  favorite_authors: string[];
  favorite_books: string[];
  reading_goal: string;
  reading_style: string;
  preferred_language: string;
  theme: string;
}

class OnboardingService {
  // ------------------------------------------------
  // Load onboarding data
  // ------------------------------------------------

  async getPreferences(): Promise<PreferenceOption[]> {
    return apiClient.get("/onboarding/preferences");
  }

  async getFavoriteAuthors(): Promise<Author[]> {
    return apiClient.get("/onboarding/authors");
  }

  async getFavoriteBooks(): Promise<Book[]> {
    return apiClient.get("/onboarding/books");
  }

  async getReadingStyles(): Promise<ReadingStyle[]> {
    return apiClient.get("/onboarding/reading-styles");
  }

  // ------------------------------------------------
  // Save each onboarding step
  // ------------------------------------------------

  async savePreferences(preferences: number[]) {
    return apiClient.post("/onboarding/preferences", {
      preferences,
    });
  }

  async saveFavoriteAuthors(authorIds: number[]) {
    return apiClient.post("/onboarding/authors", {
      authors: authorIds,
    });
  }

  async saveFavoriteBooks(bookIds: number[]) {
    return apiClient.post("/onboarding/books", {
      books: bookIds,
    });
  }

  async saveReadingStyle(styleId: number) {
    return apiClient.post("/onboarding/reading-style", {
      readingStyle: styleId,
    });
  }

  // ------------------------------------------------
  // Finish onboarding
  // ------------------------------------------------

  async completeOnboarding(data: CompleteOnboardingRequest) {
  return apiClient.post("/onboarding/onboarding/complete", data);
}
}

export const onboardingService = new OnboardingService();

export default onboardingService;