"use client";

import { useEffect, useState } from "react";
import { BookCard } from "@/components/books/BookCard";
import { bookService, type Book } from "@/lib/services/book.service";
import { mapApiBookToBook } from "@/lib/adapters/book.adapter";

export default function DiscoverPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const loadBooks = async (currentPage: number) => {
    setLoading(true);

    try {
      const response = await bookService.getBooks(currentPage, 20);

      if (currentPage === 1) {
        setBooks(response.books);
      } else {
        setBooks((prev) => [...prev, ...response.books]);
      }

      setTotal(response.total);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBooks(1);
  }, []);

  const loadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    loadBooks(nextPage);
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Discover Books</h1>
        <p className="text-muted-foreground mt-2">
          Browse {total.toLocaleString()} books from your recommendation database.
        </p>
      </div>

      {loading && books.length === 0 ? (
        <div className="py-20 text-center">Loading books...</div>
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
            <div className="flex justify-center pt-6">
              <button
                onClick={loadMore}
                disabled={loading}
                className="rounded-lg bg-black px-6 py-3 text-white hover:bg-gray-800 disabled:opacity-50"
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