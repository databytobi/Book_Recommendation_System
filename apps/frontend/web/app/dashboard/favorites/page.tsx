"use client";

import { useEffect, useState } from "react";
import { Heart } from "lucide-react";

import { BookCard } from "@/components/books/BookCard";
import {
  favoriteService,
  type FavoriteBook,
} from "@/lib/services/favorite.service";
import { mapApiBookToBook } from "@/lib/adapters/book.adapter";

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState<FavoriteBook[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadFavorites = async () => {
      try {
        const data = await favoriteService.getFavorites();
        setFavorites(data.favorites);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadFavorites();
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <div className="mb-3 flex items-center gap-2">
          <Heart className="h-6 w-6 fill-red-500 text-red-500" />
          <span className="rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-600">
            Personal Collection
          </span>
        </div>

        <h1 className="text-3xl font-bold">Favorites</h1>

        <p className="mt-2 text-muted-foreground">
          Books you've saved from recommendations, search and discovery.
        </p>
      </div>

      {loading ? (
        <div className="py-20 text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-b-2 border-primary" />
          <p className="mt-4 text-muted-foreground">Loading favorites...</p>
        </div>
      ) : favorites.length === 0 ? (
        <div className="rounded-xl border border-dashed p-16 text-center">
          <Heart className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />
          <h3 className="text-lg font-semibold">No favorites yet</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Tap the heart icon on any book to save it here.
          </p>
        </div>
      ) : (
        <>
          <p className="text-sm text-muted-foreground">
            {favorites.length} saved books
          </p>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5">
            {favorites.map((book) => (
              <BookCard
               key={book.isbn}
               book={mapApiBookToBook(book)}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}