"use client";

import { useEffect, useState } from "react";
import { History } from "lucide-react";

import { BookCard } from "@/components/books/BookCard";
import {
  historyService,
  type HistoryBook,
} from "@/lib/services/history.service";

import { mapApiBookToBook } from "@/lib/adapters/book.adapter";


export default function HistoryPage() {
  const [books, setBooks] = useState<HistoryBook[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    historyService
      .getHistory()
      .then((res) => setBooks(res.history))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <div className="mb-3 flex items-center gap-2">
          <History className="h-6 w-6 text-primary" />
          <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
            Reading Timeline
          </span>
        </div>

        <h1 className="text-3xl font-bold">Reading History</h1>

        <p className="mt-2 text-muted-foreground">
          Your recently read books and reading progress.
        </p>
      </div>

      {loading ? (
        <div className="py-20 text-center">Loading...</div>
      ) : books.length === 0 ? (
        <div className="rounded-xl border border-dashed p-16 text-center">
          No reading history yet.
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5">
          {books.map((book) => (
            <BookCard
             key={book.isbn}
             book={mapApiBookToBook(book)}
             />
          ))}
        </div>
      )}
    </div>
  );
}