"use client";

import { useEffect, useState } from "react";
import { AuthGuard } from "@/features/auth/guard";

import {
  DashboardGrid,
  WelcomeCard,
  StatsCard,
} from "@/components/dashboard";

import { ContinueReading } from "@/components/reading/ContinueReading";
import { ReadingGoal } from "@/components/reading/ReadingGoal";
import { RecentlyViewed } from "@/components/reading/RecentlyViewed";

import { RecommendationSection } from "@/components/recommendations/RecommendationSection";
import { BookCard } from "@/components/books/BookCard";

import { useDashboard } from "@/hooks";
import { dashboardIcons } from "@/lib/constants";

// ============================================================
// Debug
// ============================================================

if (typeof window !== "undefined") {
  const dashboardWindow = window as Window & {
    __dashboardRenderCount?: number;
  };

  const renderCount = dashboardWindow.__dashboardRenderCount ?? 0;

  dashboardWindow.__dashboardRenderCount = renderCount + 1;

  console.log(`Dashboard render #${renderCount + 1}`);
}

// FIX 3: Replace 'any' with proper type
const isValidBook = (
  book: { id?: string | number } | null | undefined
) => {
  if (!book) return false;

  const id = Number(book.id);

  return !Number.isNaN(id) && id > 0;
};

export default function DashboardPage() {
  const { dashboard, loading, error } = useDashboard();

  // FIX: Move state to top level - track visibility per section
  const [visibleCounts, setVisibleCounts] = useState<Record<string, number>>({});

  const getVisibleCount = (sectionId: string) => {
    return visibleCounts[sectionId] || 4;
  };

  const loadMore = (sectionId: string, currentVisible: number) => {
    setVisibleCounts((prev) => ({
      ...prev,
      [sectionId]: currentVisible + 4,
    }));
  };

  useEffect(() => {
    console.log("Dashboard", dashboard);
  }, [dashboard]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-b-2 border-primary" />
          <p className="mt-4 text-sm text-muted-foreground">
            Loading your dashboard...
          </p>
        </div>
      </div>
    );
  }

  if (error || !dashboard) {
    return (
      <div className="flex items-center justify-center py-20 text-red-500">
        Something went wrong while loading your dashboard.
      </div>
    );
  }

  // ============================================================
  // Continue Reading
  // ============================================================

  const continueReadingBooks = (dashboard.continueReading || [])
    .filter(isValidBook)
    .map((book) => ({
      id: String(book.id),
      title: book.title || "Untitled",
      author: book.author?.name || "Unknown Author",
      coverUrl: book.cover ?? undefined,
      rating: book.rating ?? undefined,
      progress: book.progress?.percentage ?? 0,
      currentPage: book.progress?.currentPage ?? 0,
      totalPages: book.progress?.totalPages ?? 0,
      lastReadAt:
        book.progress?.lastReadAt ?? new Date().toISOString(),
      estimatedTimeLeft:
        book.timeLeftDisplay ?? "Unknown",
    }));

  // ============================================================
  // Recently Viewed
  // ============================================================

  const recentlyViewedBooks = (dashboard.recentlyViewed || [])
    .filter(isValidBook)
    .map((book) => ({
      id: String(book.id),
      title: book.title || "Untitled",
      author: book.author?.name || "Unknown Author",
      coverUrl: book.cover ?? undefined,
      rating: book.rating ?? undefined,
      viewedAt:
        book.viewedAt ?? new Date().toISOString(),
      isInLibrary: true,
    }));

  // ============================================================
  // Reading Goal
  // ============================================================

  const readingGoal =
    dashboard.readingGoal &&
    dashboard.readingGoal.goalType === "books"
      ? {
          yearlyGoal: dashboard.readingGoal.target || 0,
          booksRead: dashboard.readingGoal.current || 0,
        }
      : null;

  // ============================================================
  // Recommendations
  // ============================================================

  const recommendationSections = (dashboard.recommendations || [])
    .map((section) => ({
      ...section,
      books: (section.books || [])
        .filter(isValidBook)
        .map((book) => ({
          book: {
            id: String(book.id),
            title: book.title || "Untitled",
            author: book.author?.name || "Unknown Author",
            coverImage: book.cover ?? undefined,
            averageRating: book.rating ?? 0,
            ratingsCount: 0,
            genres: [],
            isFavorite: false,
            isInLibrary: false,
          },
          href: `/books/${book.id}`,
          showActions: true,
          showProgress: false,
          showGenres: false,
          showDescription: false,
          variant: "default" as const,
          size: "md" as const,
        })),
    }))
    .filter((section) => section.books.length > 0);

  // FIX: Wrap console.log in development check
  if (process.env.NODE_ENV === "development") {
    console.log({
      continueReadingBooks,
      recentlyViewedBooks,
      recommendationSections,
      readingGoal,
    });
  }

  return (
    <AuthGuard>
      <div className="space-y-6">
        {/* ========================================================== */}
        {/* Welcome */}
        {/* ========================================================== */}
        <WelcomeCard />

        {/* ========================================================== */}
        {/* Stats */}
        {/* ========================================================== */}
        <DashboardGrid columns={{ default: 1, sm: 2, lg: 4 }}>
          {(dashboard.stats || []).map((stat) => {
            const Icon =
              stat.icon && dashboardIcons[stat.icon]
                ? dashboardIcons[stat.icon]
                : dashboardIcons.bookOpen;

            return (
              <StatsCard
                key={stat.title}
                title={stat.title}
                value={stat.value}
                description={stat.description}
                trend={
                  stat.change !== undefined
                    ? `${stat.change > 0 ? "+" : ""}${stat.change}%`
                    : undefined
                }
                icon={<Icon className="h-5 w-5" />}
              />
            );
          })}
        </DashboardGrid>

        {/* ========================================================== */}
        {/* Continue Reading + Goal */}
        {/* ========================================================== */}

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
          <div className="xl:col-span-2">
            {continueReadingBooks.length > 0 ? (
              <ContinueReading
                books={continueReadingBooks}
                loading={false}
              />
            ) : (
              <div className="rounded-xl border border-dashed p-8 text-center text-muted-foreground">
                No books currently in progress.
              </div>
            )}
          </div>

          <div>
            {readingGoal ? (
              <ReadingGoal
                yearlyGoal={readingGoal.yearlyGoal}
                booksRead={readingGoal.booksRead}
              />
            ) : (
              <div className="rounded-xl border border-dashed p-8 text-center text-muted-foreground">
                No reading goal set.
              </div>
            )}
          </div>
        </div>

        {/* ========================================================== */}
        {/* Recently Viewed */}
        {/* ========================================================== */}

        {recentlyViewedBooks.length > 0 && (
          <RecentlyViewed
            books={recentlyViewedBooks}
            loading={false}
          />
        )}

        {/* ========================================================== */}
        {/* Recommendations */}
        {/* ========================================================== */}

        {recommendationSections.length > 0 &&
          recommendationSections.map((section) => {
            const visible = getVisibleCount(section.id);

            return (
              <RecommendationSection
                key={section.id}
                title={section.title}
                description={section.description}
                href={section.viewAllLink || "#"}
                variant={section.featured ? "featured" : "default"}
                badge={section.featured ? "AI Pick" : undefined}
              >
                <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                  {section.books.slice(0, visible).map((item) => (
                    <BookCard
                      key={item.book.id}
                      book={item.book as any}
                      href={item.href}
                      variant="default"
                      size="md"
                      showActions
                    />
                  ))}
                </div>

                {visible < section.books.length && (
                  <div className="mt-6 flex justify-center">
                    <button
                      onClick={() => loadMore(section.id, visible)}
                      className="rounded-lg border px-4 py-2 text-sm hover:bg-muted"
                    >
                      Load 4 More Books
                    </button>
                  </div>
                )}
              </RecommendationSection>
            );
          })}
      </div>
    </AuthGuard>
  );
}