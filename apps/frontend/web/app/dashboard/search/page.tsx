"use client";

import { useEffect, useState } from "react";
import { Search } from "lucide-react";

import { searchService } from "@/lib/services/search.service";
import { BookCard } from "@/components/books/BookCard";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [books, setBooks] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const performSearch = async (value: string) => {
    if (value.trim().length < 2) {
      setBooks([]);
      return;
    }

    setLoading(true);

    try {
      const response = await searchService.searchBooks(value);
      setBooks(response.results);
    } catch (err) {
      console.error(err);
      setBooks([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      performSearch(query);
    }, 400);

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Search Books</h1>
        <p className="mt-2 text-muted-foreground">
          Search across 248,176 books by title or author.
        </p>
      </div>

      <div className="relative max-w-2xl">
        <Search className="absolute left-4 top-3.5 h-5 w-5 text-muted-foreground" />

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by title or author..."
          className="w-full rounded-xl border bg-background py-3 pl-12 pr-4 outline-none focus:ring-2 focus:ring-primary"
        />
      </div>

      {loading && (
        <p className="text-sm text-muted-foreground">Searching...</p>
      )}

      {!loading && query.length >= 2 && books.length === 0 && (
        <div className="rounded-xl border border-dashed py-16 text-center">
          <Search className="mx-auto mb-4 h-10 w-10 text-muted-foreground" />
          <h3 className="text-lg font-semibold">No books found</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Try another title or author.
          </p>
        </div>
      )}

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5">
        {books.map((result) => (
          <BookCard
            key={result.book.id}
            book={result.book}
          />
        ))}
      </div>
    </div>
  );
}