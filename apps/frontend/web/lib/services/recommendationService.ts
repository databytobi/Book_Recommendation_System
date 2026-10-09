import { tokenStorage } from "@/services/storage/token";

const API_BASE = "http://127.0.0.1:8000/api/v1";

export interface RecommendedBook {
  isbn: string;
  title: string;
  authors: string | null;
  genre: string | null;
  publisher: string | null;
  publication_year: number | null;
  average_rating: number;
  ratings_count: number;
  image_url: string | null;
  recommendation_score: number;
  recommendation_reason: string;
}

export interface RecommendationResponse {
  success: boolean;
  total: number;
  generated_from: string;
  recommendations: RecommendedBook[];
}

export async function getRecommendations(
  limit = 20
): Promise<RecommendationResponse> {
  const token = tokenStorage.getAccessToken();

  const response = await fetch(
    `${API_BASE}/recommendations?limit=${limit}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch recommendations");
  }

  return response.json();
}