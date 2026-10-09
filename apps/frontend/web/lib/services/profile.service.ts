import { tokenStorage } from "@/services/storage/token";

const API_BASE = "http://127.0.0.1:8000/api/v1";

const authHeaders = () => ({
  Authorization: `Bearer ${tokenStorage.getAccessToken()}`,
});

export interface UserProfile {
  id: number;
  full_name: string;
  email: string;
  created_at: string;
}

export interface ProfileSummary {
  user: UserProfile;
  favorites: number;
  booksRead: number;
}

class ProfileService {
  async getProfile(): Promise<ProfileSummary> {
    const token = tokenStorage.getAccessToken();

    const [userRes, favRes, historyRes] = await Promise.all([
      fetch(`${API_BASE}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }),
      fetch(`${API_BASE}/favorites`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
      fetch(`${API_BASE}/history`, {
        headers: { Authorization: `Bearer ${token}` },
      }),
    ]);

    if (!userRes.ok) {
      const err = await userRes.text();
      console.error("auth/me failed:", userRes.status, err);
      throw new Error("Failed to load profile");
    }

    const user = await userRes.json();
    const favorites = favRes.ok ? await favRes.json() : { total: 0 };
    const history = historyRes.ok ? await historyRes.json() : { total: 0 };

    return {
      user,
      favorites: favorites.total ?? 0,
      booksRead: history.total ?? 0,
    };
  }
}

export const profileService = new ProfileService();