"use client";

import { useEffect, useState } from "react";
import { Library, BookOpen } from "lucide-react";

import { bookService, type Book } from "@/lib/services/book.service";
import { BookCard } from "@/components/books/BookCard";
import { mapApiBookToBook } from "@/lib/adapters/book.adapter";

export default function LibraryPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const loadBooks = async (pageNumber = 1) => {
    try {
      setLoading(true);

      const response = await bookService.getBooks(pageNumber, 24);

      if (pageNumber === 1) {
        setBooks(response.books);
      } else {
        setBooks((prev) => [...prev, ...response.books]);
      }

      setTotal(response.total);
      setPage(response.page);
    } catch (err) {
      console.error("Failed to load library:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBooks(1);
  }, []);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="mb-3 flex items-center gap-2">
          <Library className="h-6 w-6 text-primary" />
          <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
            248,176 Books
          </span>
        </div>

        <h1 className="text-3xl font-bold">Library</h1>

        <p className="mt-2 text-muted-foreground">
          Browse the complete book collection available in your recommendation platform.
        </p>
      </div>

      {/* Stats */}
      <div className="rounded-xl border bg-card p-5">
        <div className="flex items-center gap-3">
          <BookOpen className="h-10 w-10 text-primary" />
          <div>
            <p className="text-sm text-muted-foreground">Books Available</p>
            <h2 className="text-2xl font-bold">
              {total.toLocaleString()}
            </h2>
          </div>
        </div>
      </div>

      {/* Books */}
      {loading && books.length === 0 ? (
        <div className="py-20 text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-b-2 border-primary" />
          <p className="mt-4 text-muted-foreground">
            Loading library...
          </p>
        </div>
      ) : (
        <>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5">
            {books.map((book) => (
              <BookCard
              key={book.isbn}
              book={mapApiBookToBook(book)}
            />
            ))}
          </div>

          {books.length < total && (
            <div className="flex justify-center pt-4">
              <button
                onClick={() => loadBooks(page + 1)}
                disabled={loading}
                className="rounded-lg border px-6 py-3 font-medium hover:bg-muted disabled:opacity-50"
              >
                {loading ? "Loading..." : "Load More"}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}