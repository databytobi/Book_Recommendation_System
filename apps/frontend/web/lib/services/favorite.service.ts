import { tokenStorage } from "@/services/storage/token";

const API_BASE = "http://127.0.0.1:8000/api/v1";

export interface FavoriteBook {
  isbn: string;
  title: string;
  authors: string;
  image_url: string | null;
  average_rating: number | null;
  ratings_count: number | null;
  added_at: string;
}

export interface FavoriteResponse {
  success: boolean;
  message: string;
}

export interface FavoriteListResponse {
  success: boolean;
  total: number;
  favorites: FavoriteBook[];
}

const authHeaders = () => ({
  Authorization: `Bearer ${tokenStorage.getAccessToken()}`,
  "Content-Type": "application/json",
});

class FavoriteService {
  async getFavorites(): Promise<FavoriteListResponse> {
    const res = await fetch(`${API_BASE}/favorites`, {
      headers: authHeaders(),
    });

    if (!res.ok) throw new Error("Failed to fetch favorites");

    return res.json();
  }

  async addFavorite(isbn: string): Promise<FavoriteResponse> {
    const res = await fetch(`${API_BASE}/favorites/${isbn}`, {
      method: "POST",
      headers: authHeaders(),
    });

    if (!res.ok) throw new Error("Failed to add favorite");

    return res.json();
  }

  async removeFavorite(isbn: string): Promise<FavoriteResponse> {
    const res = await fetch(`${API_BASE}/favorites/${isbn}`, {
      method: "DELETE",
      headers: authHeaders(),
    });

    if (!res.ok) throw new Error("Failed to remove favorite");

    return res.json();
  }
}

export const favoriteService = new FavoriteService();