import { apiClient } from "@/lib/api/client";

export interface UserSettings {
  preferred_genres: string[];
  favorite_authors: string[];
  favorite_books: string[];
  reading_goal: string;
  reading_style: string;
  preferred_language: string;
  theme: string;
}

class SettingsService {
  async getSettings(): Promise<UserSettings> {
    return apiClient.get("/onboarding/onboarding/preferences");
  }

  async updateSettings(data: UserSettings) {
    return apiClient.post("/onboarding/onboarding/complete", data);
  }
}

export const settingsService = new SettingsService();