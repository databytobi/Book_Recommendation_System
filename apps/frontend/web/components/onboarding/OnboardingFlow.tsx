"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation"; // Step 1: Added import

import { WelcomeStep } from "./WelcomeStep";
import {
  FavoriteAuthorsStep,
  Author,
} from "./FavoriteAuthorsStep";
import {
  FavoriteBooksStep,
  FavoriteBook,
} from "./FavoriteBooksStep";
import {
  PreferencesStep,
  PreferenceValues,
} from "./PreferencesStep";
import {
  ReadingStyleStep,
  ReadingStyleOption,
  ReadingStyle,
} from "./ReadingStyleStep";
import { Button } from "@/components/ui/button";
import { useUser } from "@/features/auth/useAuth";

// FIX: Removed saveOnboardingProgress import
import { apiClient } from "@/lib/api/client";
// FIX: Added import for onboardingService
import onboardingService from "@/lib/services/onboarding.service";

type Step =
  | "welcome"
  | "authors"
  | "books"
  | "preferences"
  | "reading-style"
  | "complete";

interface BookSearchResult {
  isbn: string;
  title: string;
  authors: string[];
  publication_year?: number | null;
  image_url?: string | null;
  average_rating?: number | null;
  ratings_count?: number | null;
}

interface BookSearchResponse {
  results: BookSearchResult[];
  total: number;
}

export function OnboardingFlow() {
  const router = useRouter(); // Step 2: Initialized router
  const user = useUser();
  const [step, setStep] = useState<Step>("welcome");

  // Greet the signed-in user by name.
  // Previously the welcome step received a hardcoded userName="Bruno", so
  // EVERY new account was greeted as "Bruno". Prefer the name captured at
  // registration (full_name), then fall back to username, and finally to a
  // neutral greeting handled by WelcomeStep itself.
  const userName =
    user?.full_name?.trim() || user?.username?.trim() || undefined;

  // Step 1: Create one onboarding state
  const [onboardingData, setOnboardingData] = useState({
    preferred_genres: [] as string[],
    favorite_authors: [] as string[],
    favorite_books: [] as string[],
    reading_goal: "moderate",
    reading_style: "balanced" as ReadingStyle,
    preferred_language: "en",
    theme: "dark",
  });

  const [books, setBooks] = useState<FavoriteBook[]>([]);
  const [booksLoading, setBooksLoading] = useState(false);
  const [booksError, setBooksError] = useState<string | null>(null);

  const [selectedReadingStyle, setSelectedReadingStyle] =
    useState<ReadingStyle | null>(null);

  const readingStyles: ReadingStyleOption[] = [
    {
      id: "quick",
      title: "Quick Reader",
      description:
        "I prefer shorter reading sessions and books I can finish relatively quickly.",
    },
    {
      id: "balanced",
      title: "Balanced Reader",
      description:
        "I enjoy a mix of shorter and longer books at a comfortable pace.",
    },
    {
      id: "deep",
      title: "Deep Reader",
      description:
        "I enjoy taking my time with detailed, complex, and immersive books.",
    },
    {
      id: "explorer",
      title: "Reading Explorer",
      description:
        "I enjoy discovering different genres, authors, and new kinds of books.",
    },
  ];

  const authors: Author[] = [
    {
      id: 1,
      name: "J.K. Rowling",
      books_count: 18,
    },
    {
      id: 2,
      name: "Stephen King",
      books_count: 72,
    },
    {
      id: 3,
      name: "Agatha Christie",
      books_count: 80,
    },
    {
      id: 4,
      name: "Jane Austen",
      books_count: 6,
    },
    {
      id: 5,
      name: "George R.R. Martin",
      books_count: 15,
    },
    {
      id: 6,
      name: "Brandon Sanderson",
      books_count: 40,
    },
    {
      id: 7,
      name: "Rick Riordan",
      books_count: 32,
    },
    {
      id: 8,
      name: "Neil Gaiman",
      books_count: 24,
    },
  ];

  function isValidISBN10(isbn: string): boolean {
    const normalized = isbn
      .replace(/[-\s]/g, "")
      .toUpperCase();

    if (!/^\d{9}[\dX]$/.test(normalized)) {
      return false;
    }

    let sum = 0;

    for (let i = 0; i < 10; i++) {
      const value =
        normalized[i] === "X"
          ? 10
          : Number(normalized[i]);

      sum += value * (10 - i);
    }

    return sum % 11 === 0;
  }

  /**
   * Load books from the backend.
   */
  async function loadBooks() {
    setBooksLoading(true);
    setBooksError(null);

    try {
      const response =
        (await apiClient.get(
          "/books/search?q=the&limit=20"
        )) as BookSearchResponse;

      const validResults = response.results.filter(
        (book) => {
          const valid = isValidISBN10(book.isbn);

          if (!valid) {
            console.warn(
              "Skipping book with invalid ISBN:",
              book.isbn,
              book.title
            );
          }

          return valid;
        }
      );

      const mappedBooks: FavoriteBook[] =
        validResults.map((book) => ({
          id: book.isbn,
          isbn: book.isbn,
          title: book.title,
          author:
            book.authors &&
            book.authors.length > 0
              ? book.authors.join(", ")
              : "Unknown Author",
          cover_url: book.image_url ?? null,
          average_rating:
            book.average_rating ?? undefined,
        }));

      setBooks(mappedBooks);
    } catch (error) {
      console.error(
        "Failed to load books:",
        error
      );

      setBooksError(
        "Unable to load books. Please try again."
      );
    } finally {
      setBooksLoading(false);
    }
  }

  /**
   * Load books when the user reaches
   * the Favorite Books step.
   */
  useEffect(() => {
    if (
      step === "books" &&
      books.length === 0
    ) {
      loadBooks();
    }
  }, [step, books.length]);

  /**
   * Save selected authors and move
   * to Favorite Books.
   */
  // Step 2: Updated Authors step
  const handleAuthorsContinue = async (selected: number[]) => {
    const selectedAuthors = authors
      .filter((author) => selected.includes(author.id))
      .map((author) => author.name);

    setOnboardingData((prev) => ({
      ...prev,
      favorite_authors: selectedAuthors,
    }));

    setStep("books");
  };

  /**
   * Save selected books and move
   * to Preferences.
   */
  // Step 3: Updated Books step
  const handleBooksContinue = async (selectedBookIds: string[]) => {
    setOnboardingData((prev) => ({
      ...prev,
      favorite_books: selectedBookIds,
    }));

    setStep("preferences");
  };

  /**
   * Save reading preferences and
   * move to the next onboarding step.
   */
  // Step 4: Updated Preferences - keep as is
  const handlePreferencesContinue = async (
    values: PreferenceValues
  ) => {
    setOnboardingData((prev) => ({
      ...prev,
      reading_goal: values.reading_goal,
      preferred_language: values.preferred_language,
      theme: values.theme,
    }));

    setStep("reading-style");
  };

  /**
   * Save reading style and move
   * to Complete.
   */
  // Step 5: Updated Reading Style step
  const handleReadingStyleContinue = async (
    style: ReadingStyle
  ) => {
    try {
      const payload = {
        ...onboardingData,
        reading_style: style,
      };

      await onboardingService.completeOnboarding(payload);

      setOnboardingData(payload);
      setSelectedReadingStyle(style);

      setStep("complete");
    } catch (error) {
      console.error(
        "Failed to complete onboarding:",
        error
      );
    }
  };

  /**
   * Retry loading books.
   */
  const handleBooksRetry = () => {
    loadBooks();
  };

  // Step 3: Auto-redirect after completion
  const isCompleted = step === "complete";

  useEffect(() => {
    if (!isCompleted) return;

    const timer = setTimeout(() => {
      router.replace("/dashboard");
    }, 1800);

    return () => clearTimeout(timer);
  }, [isCompleted, router]);

  return (
    <div className="w-full">
      {step === "welcome" && (
        <WelcomeStep
          userName={userName}
          onStart={() =>
            setStep("authors")
          }
        />
      )}

      {step === "authors" && (
        <FavoriteAuthorsStep
          authors={authors}
          minimumSelection={3}
          onContinue={
            handleAuthorsContinue
          }
        />
      )}

      {step === "books" && (
        <FavoriteBooksStep
          books={books}
          loading={booksLoading}
          error={booksError}
          minimumSelection={5}
          onContinue={
            handleBooksContinue
          }
          onRetry={handleBooksRetry}
        />
      )}

      {/* FIX: Replaced preferences step with PreferencesStep component */}
      {step === "preferences" && (
        <PreferencesStep
          onContinue={handlePreferencesContinue}
        />
      )}

      {step === "reading-style" && (
        <ReadingStyleStep
          styles={readingStyles}
          loading={false}
          error={null}
          initialSelection={selectedReadingStyle}
          onContinue={handleReadingStyleContinue}
        />
      )}

      {step === "complete" && (
        <div className="mx-auto max-w-2xl rounded-3xl border bg-card p-10 text-center shadow-lg">
          <h2 className="text-3xl font-bold">
            You&apos;re All Set!
          </h2>

          <p className="mt-4 text-muted-foreground">
            Your reading preferences have been saved.
            We&apos;re ready to personalize your recommendations.
          </p>

          {/* Step 4: Added manual button and auto-redirect message */}
          <button
            onClick={() => router.replace("/dashboard")}
            className="mt-6 w-full rounded-lg bg-primary py-3 text-primary-foreground font-medium hover:opacity-90 transition"
          >
            Go to Dashboard
          </button>

          <p className="mt-3 text-xs text-center text-muted-foreground">
            Redirecting automatically…
          </p>
        </div>
      )}
    </div>
  );
}