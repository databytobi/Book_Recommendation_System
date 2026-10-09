import { tokenStorage } from "@/services/storage/token";

const API_BASE = "http://127.0.0.1:8000/api/v1";

export interface HistoryBook {
  isbn: string;
  title: string;
  authors: string;
  image_url: string | null;
  progress: number;
  rating: number | null;
  last_read_at: string;
}

export interface HistoryResponse {
  success: boolean;
  total: number;
  history: HistoryBook[];
}

export const historyService = {
  async getHistory(): Promise<HistoryResponse> {
    const token = tokenStorage.getAccessToken();

    const res = await fetch(`${API_BASE}/history`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!res.ok) {
      throw new Error("Failed to load reading history");
    }

    return res.json();
  },
};