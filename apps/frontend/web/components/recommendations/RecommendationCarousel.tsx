// apps/frontend/web/components/recommendations/RecommendationCarousel.tsx

"use client";

import {
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import { BookCard } from "@/components/books";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

// ==========================================================
// TYPES
// ==========================================================

export interface CarouselBook {
  id: string | number;
  title: string;
  author: string;
  coverImage?: string;

  averageRating?: number;
  ratingsCount?: number;

  genres?: string[];

  progress?: number;

  description?: string;

  isFavorite?: boolean;
  isInLibrary?: boolean;
}

export interface RecommendationCarouselItem {
  book: CarouselBook;

  href?: string;

  variant?: "default" | "compact" | "horizontal" | "featured";

  size?: "sm" | "md" | "lg";

  showActions?: boolean;

  showGenres?: boolean;

  showProgress?: boolean;

  showDescription?: boolean;

  priority?: boolean;

  onFavorite?: () => void;

  onLibrary?: () => void;

  onView?: () => void;

  onMore?: () => void;

  onQuickView?: () => void;
}

interface RecommendationCarouselProps {
  books: RecommendationCarouselItem[];

  className?: string;

  title?: string;

  autoplay?: boolean;

  autoplayInterval?: number;

  showDots?: boolean;

  showProgress?: boolean;
}

// ==========================================================
// COMPONENT
// ==========================================================

export function RecommendationCarousel({
  books,
  className,
  title,

  autoplay = false,

  autoplayInterval = 5000,

  showDots = true,

  showProgress = true,
}: RecommendationCarouselProps) {

  // ========================================================
  // REFS
  // ========================================================

  const containerRef = useRef<HTMLDivElement>(null);

  const autoplayTimer = useRef<NodeJS.Timeout | null>(null);

  const progressTimer = useRef<NodeJS.Timeout | null>(null);

  // ========================================================
  // STATE
  // ========================================================

  const [scrollPosition, setScrollPosition] = useState(0);

  const [maxScroll, setMaxScroll] = useState(0);

  const [isHovered, setIsHovered] = useState(false);

  const [progress, setProgress] = useState(0);

  // ========================================================
  // MEMOIZED VALUES
  // ========================================================

  const CARD_WIDTH = 250;

  const currentSlide = useMemo(() => {
    return Math.round(scrollPosition / CARD_WIDTH);
  }, [scrollPosition]);

  const totalSlides = books.length;

  const canScrollLeft = scrollPosition > 5;

  const canScrollRight = scrollPosition < maxScroll - 5;

  // ========================================================
  // HELPERS
  // ========================================================

  const updateScrollState = useCallback(() => {
    const container = containerRef.current;

    if (!container) return;

    setScrollPosition(container.scrollLeft);

    setMaxScroll(container.scrollWidth - container.clientWidth);
  }, []);

  const scroll = useCallback(
    (direction: "left" | "right") => {
      const container = containerRef.current;

      if (!container) return;

      const amount = CARD_WIDTH * 3;

      container.scrollBy({
        left: direction === "left" ? -amount : amount,
        behavior: "smooth",
      });
    },
    []
  );

  const scrollToIndex = useCallback((index: number) => {
    const container = containerRef.current;

    if (!container) return;

    setProgress(0);

    container.scrollTo({
      left: index * CARD_WIDTH,
      behavior: "smooth",
    });
  }, []);

  // ========================================================
  // AUTOPLAY
  // ========================================================

  useEffect(() => {
    if (!autoplay) return;

    if (isHovered) return;

    if (totalSlides <= 1) return;

    autoplayTimer.current = setInterval(() => {
      const nextSlide =
        currentSlide >= totalSlides - 1
          ? 0
          : currentSlide + 1;

      scrollToIndex(nextSlide);
    }, autoplayInterval);

    return () => {
      if (autoplayTimer.current) {
        clearInterval(autoplayTimer.current);
      }
    };
  }, [
    autoplay,
    autoplayInterval,
    currentSlide,
    totalSlides,
    isHovered,
    scrollToIndex,
  ]);

  // ========================================================
  // PROGRESS BAR
  // ========================================================

  useEffect(() => {
    if (!autoplay) return;

    if (isHovered) return;

    const interval = 50;

    const increment =
      100 / (autoplayInterval / interval);

    progressTimer.current = setInterval(() => {
      setProgress(previous => {
        if (previous >= 100) return 0;

        return previous + increment;
      });
    }, interval);

    return () => {
      if (progressTimer.current) {
        clearInterval(progressTimer.current);
      }
    };
  }, [
    autoplay,
    autoplayInterval,
    currentSlide,
    isHovered,
  ]);

  // ========================================================
  // RESIZE + SCROLL
  // ========================================================

  useEffect(() => {
    updateScrollState();

    const handleResize = () => {
      updateScrollState();
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener(
        "resize",
        handleResize
      );
    };
  }, [updateScrollState]);

  useEffect(() => {
    const container = containerRef.current;

    if (!container) return;

    container.addEventListener(
      "scroll",
      updateScrollState
    );

    return () => {
      container.removeEventListener(
        "scroll",
        updateScrollState
      );
    };
  }, [updateScrollState]);

  // ========================================================
  // EMPTY STATE
  // ========================================================

  if (books.length === 0) {
    return (
      <div className="flex h-56 items-center justify-center rounded-xl border border-dashed">
        <p className="text-sm text-muted-foreground">
          No recommendations available.
        </p>
      </div>
    );
  }

  // ========================================================
  // BOOK MAPPER - FIXED
  // ========================================================

  const mapBookProps = (
    item: RecommendationCarouselItem
  ) => ({
    ...item,
    book: {
      id: String(item.book.id),
      title: item.book.title,
      author: {
        id: String(item.book.id),
        name: item.book.author,
      },
      coverImage: item.book.coverImage,
      averageRating:
        item.book.averageRating ?? 0,
      ratingsCount:
        item.book.ratingsCount ?? 0,
      genres: item.book.genres ?? [],
      progress: item.book.progress,
      description: item.book.description,
      isFavorite:
        item.book.isFavorite ?? false,
      isInLibrary:
        item.book.isInLibrary ?? false,
    },
  });

  return (
    <div
      className={cn("relative space-y-5", className)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* HEADER */}

      {title && (
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold tracking-tight">
            {title}
          </h3>

          {showProgress && (
            <span className="text-xs text-muted-foreground">
              {currentSlide + 1} / {totalSlides}
            </span>
          )}
        </div>
      )}

      {/* CAROUSEL */}

      <div className="relative group">

        {/* Left Button */}

        <Button
          variant="outline"
          size="icon"
          onClick={() => scroll("left")}
          disabled={!canScrollLeft}
          className={cn(
            "absolute left-2 top-1/2 z-20 hidden -translate-y-1/2 rounded-full bg-background/90 shadow-lg backdrop-blur md:flex",
            !canScrollLeft &&
              "pointer-events-none opacity-0"
          )}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>

        {/* Right Button */}

        <Button
          variant="outline"
          size="icon"
          onClick={() => scroll("right")}
          disabled={!canScrollRight}
          className={cn(
            "absolute right-2 top-1/2 z-20 hidden -translate-y-1/2 rounded-full bg-background/90 shadow-lg backdrop-blur md:flex",
            !canScrollRight &&
              "pointer-events-none opacity-0"
          )}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>

        {/* SCROLL CONTAINER */}

        <div
          ref={containerRef}
          className="
            flex
            gap-5
            overflow-x-auto
            scroll-smooth
            pb-4
            scrollbar-hide
          "
          style={{
            scrollbarWidth: "none",
            msOverflowStyle: "none",
          }}
        >
          {books.map((item, index) => {
            const props = mapBookProps(item);

            return (
              <div
                key={`${item.book.id}-${index}`}
                className="
                  min-w-[230px]
                  max-w-[230px]
                  flex-shrink-0
                  transition-transform
                  duration-300
                  hover:scale-[1.02]
                "
              >
                <BookCard {...props} />
              </div>
            );
          })}
        </div>

        {/* EDGE GRADIENTS */}

        <div className="pointer-events-none absolute inset-y-0 left-0 w-10 bg-gradient-to-r from-background to-transparent" />

        <div className="pointer-events-none absolute inset-y-0 right-0 w-10 bg-gradient-to-l from-background to-transparent" />
      </div>

      {/* DOT INDICATORS */}

      {showDots && totalSlides > 1 && (
        <div className="flex justify-center gap-2">
          {Array.from({
            length: Math.min(totalSlides, 10),
          }).map((_, index) => {
            const active = index === currentSlide;

            return (
              <button
                key={index}
                type="button"
                aria-label={`Go to slide ${index + 1}`}
                onClick={() => scrollToIndex(index)}
                className={cn(
                  "h-2 rounded-full transition-all duration-300",
                  active
                    ? "w-7 bg-primary"
                    : "w-2 bg-muted-foreground/30 hover:bg-muted-foreground/60"
                )}
              />
            );
          })}

          {totalSlides > 10 && (
            <span className="ml-2 text-xs text-muted-foreground">
              +{totalSlides - 10}
            </span>
          )}
        </div>
      )}

      {/* AUTOPLAY PROGRESS */}

      {autoplay &&
        showProgress &&
        !isHovered && (
          <div className="h-1 w-full overflow-hidden rounded-full bg-muted">
            <div
              className="h-full bg-primary transition-all duration-75 ease-linear"
              style={{
                width: `${progress}%`,
              }}
            />
          </div>
        )}
    </div>
  );
}