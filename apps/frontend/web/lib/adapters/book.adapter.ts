// lib/adapters/book.adapter.ts

import type { Book as ApiBook } from "@/lib/services/book.service";
import type { Book as UIBook } from "@/lib/types"; 

/**
 * Converts a book returned by the backend API
 * into the Book shape expected by frontend UI components.
 *
 * Supports authors as either:
 * - string[]
 * - string
 */
export function mapApiBookToBook(
  book: ApiBook | (Omit<ApiBook, "authors"> & { authors: string })
): UIBook {
  return {
    id: book.isbn,
    title: book.title,
    author: {
      id: book.isbn,
      name: Array.isArray(book.authors)
        ? book.authors.join(", ")
        : book.authors,
    },
    cover: book.image_url ?? undefined,
    publicationYear: book.publication_year ?? undefined,
    rating: book.average_rating ?? undefined,
  };
}