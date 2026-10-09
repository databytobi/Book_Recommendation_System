//import { RecommendedBook } from "@/lib/service/recommendationService";

import {
  getRecommendations,
  type RecommendedBook,
} from "@/lib/services/recommendationService";

interface Props {
  book: RecommendedBook;
}

export default function RecommendationCard({ book }: Props) {
  return (
    <div className="rounded-xl border bg-white shadow-sm p-3 hover:shadow-md transition">
      <img
        src={book.image_url ?? "/placeholder-book.png"}
        alt={book.title}
        className="w-full h-64 object-cover rounded-lg"
      />

      <div className="mt-3 space-y-1">
        <h3 className="font-semibold line-clamp-2">
          {book.title}
        </h3>

        <p className="text-sm text-gray-600">
          {book.authors}
        </p>

        <div className="flex items-center justify-between">
          <span className="text-yellow-600 font-medium">
            ⭐ {book.average_rating.toFixed(1)}
          </span>

          <span className="text-xs text-gray-500">
            {book.ratings_count.toLocaleString()}
          </span>
        </div>

        <p className="text-xs text-blue-600 mt-2">
          {book.recommendation_reason}
        </p>
      </div>
    </div>
  );
}