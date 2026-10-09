"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import {
  BookOpen,
  Heart,
  Star,
  Eye,
  Bookmark,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface BookCoverProps {
  src?: string;
  alt: string;
  width?: number;
  height?: number;
  priority?: boolean;
  className?: string;
  readingProgress?: number;
  isFavorite?: boolean;
  isRecommended?: boolean;
  recommendationScore?: number;
  showQuickActions?: boolean;
  onFavoriteClick?: () => void;
  onQuickView?: () => void;
  onAddToList?: () => void;
  lazyLoad?: boolean;
  quality?: number;
}

export function BookCover({
  src,
  alt,
  width = 180,
  height = 260,
  priority = false,
  className,
  readingProgress,
  isFavorite = false,
  isRecommended = false,
  recommendationScore,
  showQuickActions = false,
  onFavoriteClick,
  onQuickView,
  onAddToList,
  lazyLoad = true,
  quality = 85,
}: BookCoverProps) {
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isInView, setIsInView] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const containerRef = useRef<HTMLDivElement | null>(null);
  const isMounted = useRef(true);

  // Reset image state when the source changes
  useEffect(() => {
    setHasError(false);
    setIsLoading(true);
  }, [src]);

  // Lazy loading with Intersection Observer
  useEffect(() => {
    if (!lazyLoad) {
      setIsInView(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            if (isMounted.current) {
              setIsInView(true);
            }

            observer.disconnect();
          }
        });
      },
      {
        rootMargin: "50px",
        threshold: 0.1,
      }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, [lazyLoad]);

  // Track component mount state
  useEffect(() => {
    isMounted.current = true;

    return () => {
      isMounted.current = false;
    };
  }, []);

  const showFallback = !src || hasError;

  // Amazon's old image server can reject Next.js's image optimizer.
  // unoptimized makes the browser request the image directly.
  const isAmazonImage =
    !!src &&
    (src.includes("images.amazon.com") ||
      src.includes("images-na.ssl-images-amazon.com"));

  const spineShadow =
    "linear-gradient(to right, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0) 15%, rgba(0,0,0,0) 85%, rgba(0,0,0,0.1) 100%)";

  // ============================================================
  // FALLBACK
  // ============================================================

  if (showFallback) {
    return (
      <div
        ref={containerRef}
        className={cn(
          "relative flex items-center justify-center overflow-hidden rounded-xl",
          "border border-border/50 bg-muted",
          className
        )}
        style={{
          width,
          height,
        }}
        role="img"
        aria-label={alt}
      >
        <div className="flex flex-col items-center justify-center gap-3 px-4 text-center">
          <BookOpen className="h-12 w-12 text-muted-foreground/50" />

          <div>
            <p className="text-sm font-medium text-muted-foreground">
              No Cover Available
            </p>

            <p className="mt-1 line-clamp-2 text-xs text-muted-foreground/70">
              {alt}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={cn(
        "group relative overflow-hidden rounded-xl",
        "shadow-lg transition-shadow duration-300",
        "hover:shadow-xl hover:shadow-primary/10",
        isLoading && "animate-pulse bg-muted/50",
        className
      )}
      style={{
        width,
        height,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Blur placeholder while loading */}
      {isLoading && isInView && (
        <div
          className="absolute inset-0 animate-pulse bg-gradient-to-br from-muted to-muted/50"
          style={{ backgroundSize: "200% 200%" }}
        />
      )}

      {/* Book image */}
      {isInView && (
        <Image
          src={src}
          alt={alt}
          fill
          priority={priority}
          sizes={`${width}px`}
          quality={quality}
          unoptimized={isAmazonImage}
          className={cn(
            "object-cover transition-all duration-500",
            isLoading ? "scale-105 blur-sm" : "scale-100 blur-0",
            isHovered && "scale-105"
          )}
          onError={() => {
            setHasError(true);
            setIsLoading(false);
          }}
          onLoad={() => {
            setIsLoading(false);
          }}
          loading={lazyLoad ? "lazy" : "eager"}
        />
      )}

      {/* Book spine shadow */}
      <div
        className="absolute inset-y-0 left-0 z-10 w-8 opacity-60"
        style={{
          background: spineShadow,
        }}
      />

      {/* Reading progress overlay */}
      {readingProgress !== undefined &&
        readingProgress > 0 &&
        readingProgress < 100 && (
          <div className="absolute bottom-0 left-0 right-0 z-10 h-1 bg-black/20">
            <div
              className="h-full transition-all duration-500 ease-out"
              style={{
                width: `${readingProgress}%`,
                background:
                  "linear-gradient(to right, #4f46e5, #7c3aed)",
              }}
            />
          </div>
        )}

      {/* Favorite ribbon */}
      {isFavorite && (
        <div className="absolute -right-6 top-3 z-10 flex rotate-45 items-center gap-1 bg-rose-500 px-6 py-0.5 text-[10px] font-medium text-white shadow-md">
          <Heart className="h-3 w-3 fill-white" />
          <span>Favorite</span>
        </div>
      )}

      {/* Recommendation badge */}
      {isRecommended && recommendationScore !== undefined && (
        <div className="absolute left-2 top-2 z-10">
          <Badge
            variant="default"
            className="gap-1 border-0 bg-gradient-to-r from-amber-500 to-orange-500 px-2 py-1 text-white shadow-lg"
          >
            <Star className="h-3 w-3 fill-white" />

            <span className="text-[10px] font-bold">
              {recommendationScore}% Match
            </span>

            <Sparkles className="h-2.5 w-2.5" />
          </Badge>
        </div>
      )}

      {/* Hover quick actions */}
      {showQuickActions && isHovered && (
        <div className="absolute inset-0 z-20 flex items-center justify-center gap-2 bg-black/40 backdrop-blur-sm transition-opacity duration-300">
          <Button
            size="icon"
            variant="secondary"
            className="h-9 w-9 rounded-full bg-white/90 shadow-lg transition-transform hover:scale-110 hover:bg-white"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onQuickView?.();
            }}
            aria-label="Quick view"
          >
            <Eye className="h-4 w-4" />
          </Button>

          <Button
            size="icon"
            variant="secondary"
            className={cn(
              "h-9 w-9 rounded-full shadow-lg transition-transform hover:scale-110",
              isFavorite
                ? "bg-rose-500 text-white hover:bg-rose-600"
                : "bg-white/90 hover:bg-white"
            )}
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onFavoriteClick?.();
            }}
            aria-label="Favorite"
          >
            <Heart
              className={cn(
                "h-4 w-4",
                isFavorite && "fill-white"
              )}
            />
          </Button>

          <Button
            size="icon"
            variant="secondary"
            className="h-9 w-9 rounded-full bg-white/90 shadow-lg transition-transform hover:scale-110 hover:bg-white"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onAddToList?.();
            }}
            aria-label="Add to list"
          >
            <Bookmark className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}

// ============================================================
// Lazy-loaded version
// ============================================================

interface LazyBookCoverProps
  extends Omit<BookCoverProps, "lazyLoad"> {
  rootMargin?: string;
  threshold?: number;
}

export function LazyBookCover({
  ...props
}: LazyBookCoverProps) {
  return <BookCover {...props} lazyLoad={true} />;
}

// ============================================================
// Priority version
// ============================================================

export function PriorityBookCover(
  props: BookCoverProps
) {
  return (
    <BookCover
      {...props}
      priority={true}
      lazyLoad={false}
    />
  );
}

// ============================================================
// Gallery version
// ============================================================

interface GalleryBookCoverProps extends BookCoverProps {
  index: number;
}

export function GalleryBookCover({
  index,
  ...props
}: GalleryBookCoverProps) {
  const lazyLoadDelay = Math.min(index * 200, 2000);
  const shouldLazyLoad = index > 2;

  return (
    <div
      className="transition-all duration-300"
      style={{
        animationDelay: `${lazyLoadDelay}ms`,
      }}
    >
      <BookCover
        {...props}
        lazyLoad={shouldLazyLoad}
      />
    </div>
  );
}