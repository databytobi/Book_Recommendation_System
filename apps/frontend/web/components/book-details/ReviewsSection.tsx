"use client";

import { useState } from "react";
import Image from "next/image";
import {
  Star,
  ThumbsUp,
  MessageSquare,
  Calendar,
  ChevronDown,
  Award,
  Sparkles,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface Review {
  id: string | number;
  userName: string;
  rating: number;
  comment: string;
  createdAt: string;
  helpfulCount?: number;
  verified?: boolean;
  userAvatar?: string;
  userLocation?: string;
}

interface ReviewsSectionProps {
  averageRating: number;
  totalReviews: number;
  reviews: Review[];
  className?: string;
  onLoadMore?: () => void;
  onWriteReview?: () => void;
  onHelpful?: (reviewId: string | number) => void;
  maxInitialDisplay?: number;
  loadMoreIncrement?: number;
  showSummary?: boolean;
}

function RatingDistribution() {
  // Mock distribution - in real app, this would come from API
  const distribution = [
    { stars: 5, percentage: 45 },
    { stars: 4, percentage: 30 },
    { stars: 3, percentage: 15 },
    { stars: 2, percentage: 7 },
    { stars: 1, percentage: 3 },
  ];

  return (
    <div className="flex-1 space-y-1.5">
      {distribution.map((item) => (
        <div key={item.stars} className="flex items-center gap-3">
          <div className="flex w-8 items-center gap-1">
            <span className="text-xs font-medium text-muted-foreground">
              {item.stars}
            </span>
            <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
          </div>
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-gradient-to-r from-yellow-400 to-yellow-500 transition-all duration-1000"
              style={{ width: `${item.percentage}%` }}
            />
          </div>
          <span className="w-8 text-xs text-muted-foreground">
            {item.percentage}%
          </span>
        </div>
      ))}
    </div>
  );
}

function ReviewCard({
  review,
  onHelpful,
}: {
  review: Review;
  onHelpful?: (id: string | number) => void;
}) {
  const [isHelpfulClicked, setIsHelpfulClicked] = useState(false);
  const [helpfulCount, setHelpfulCount] = useState(review.helpfulCount || 0);

  const handleHelpful = () => {
    if (!isHelpfulClicked) {
      setHelpfulCount((prev) => prev + 1);
      setIsHelpfulClicked(true);
      onHelpful?.(review.id);
    }
  };

  return (
    <div className="group rounded-2xl border bg-card p-6 transition-all hover:shadow-md hover:shadow-primary/5">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-3">
          {/* Avatar */}
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
            {review.userAvatar ? (
              <Image
                src={review.userAvatar}
                alt={review.userName}
                width={40}
                height={40}
                className="h-full w-full rounded-full object-cover"
              />
            ) : (
              review.userName.charAt(0).toUpperCase()
            )}
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-semibold">{review.userName}</h3>
              {review.verified && (
                <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-medium text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400">
                  <Award className="h-3 w-3" />
                  Verified
                </span>
              )}
            </div>

            <div className="mt-0.5 flex items-center gap-3 text-xs text-muted-foreground">
              <div className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                <span>{new Date(review.createdAt).toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                })}</span>
              </div>
              {review.userLocation && (
                <>
                  <span>•</span>
                  <span>{review.userLocation}</span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Rating */}
        <div className="flex shrink-0 items-center gap-1">
          {Array.from({ length: 5 }).map((_, index) => (
            <Star
              key={index}
              className={cn(
                "h-4 w-4 transition-colors",
                index < review.rating
                  ? "fill-yellow-400 text-yellow-400"
                  : "text-muted-foreground/30"
              )}
            />
          ))}
        </div>
      </div>

      {/* Review Content */}
      <div className="mt-4">
        <p className="leading-relaxed text-muted-foreground">
          {review.comment}
        </p>
      </div>

      {/* Footer Actions */}
      <div className="mt-5 flex items-center gap-3 border-t border-border/50 pt-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleHelpful}
          className={cn(
            "gap-2 transition-all",
            isHelpfulClicked && "text-primary"
          )}
        >
          <ThumbsUp
            className={cn(
              "h-4 w-4 transition-transform",
              isHelpfulClicked && "fill-primary",
              !isHelpfulClicked && "group-hover:scale-110"
            )}
          />
          <span>Helpful</span>
          {helpfulCount > 0 && (
            <span className="rounded-full bg-muted px-2 py-0.5 text-xs">
              {helpfulCount}
            </span>
          )}
        </Button>

        <Button variant="ghost" size="sm" className="gap-2">
          <MessageSquare className="h-4 w-4" />
          <span>Reply</span>
        </Button>
      </div>
    </div>
  );
}

export function ReviewsSection({
  averageRating,
  totalReviews,
  reviews,
  className,
  onLoadMore,
  onWriteReview,
  onHelpful,
  maxInitialDisplay = 3,
  loadMoreIncrement = 3,
  showSummary = true,
}: ReviewsSectionProps) {
  const [visibleReviews, setVisibleReviews] = useState(maxInitialDisplay);
  const [expanded, setExpanded] = useState(false);

  const displayedReviews = reviews.slice(0, visibleReviews);
  const hasMore = visibleReviews < reviews.length;
  const shouldShowLoadMore = hasMore && !expanded;

  const handleLoadMore = () => {
    if (onLoadMore) {
      onLoadMore();
      return;
    }

    const newCount = visibleReviews + loadMoreIncrement;
    if (newCount >= reviews.length) {
      setExpanded(true);
    }
    setVisibleReviews((prev) => Math.min(prev + loadMoreIncrement, reviews.length));
  };

  return (
    <section
      className={cn(
        "space-y-8",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-primary/10 p-1.5">
              <MessageSquare className="h-4 w-4 text-primary" />
            </div>
            <h2 className="text-2xl font-bold tracking-tight">
              Reader Reviews
            </h2>
            {totalReviews > 0 && (
              <span className="rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
                {totalReviews}
              </span>
            )}
          </div>
          <p className="mt-1 text-sm text-muted-foreground">
            See what readers think about this book
          </p>
        </div>

        {onWriteReview && (
          <Button onClick={onWriteReview} className="shrink-0 gap-2">
            <MessageSquare className="h-4 w-4" />
            <span className="hidden sm:inline">Write a Review</span>
          </Button>
        )}
      </div>

      {/* Rating Summary */}
      {showSummary && (
        <div className="rounded-2xl border bg-gradient-to-br from-card to-card/50 p-6 transition-all hover:shadow-md">
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:gap-8">
            {/* Average Rating */}
            <div className="flex shrink-0 flex-col items-center justify-center gap-1">
              <div className="flex items-center gap-2">
                <Star className="h-10 w-10 fill-yellow-400 text-yellow-400" />
                <span className="text-5xl font-bold tracking-tight">
                  {averageRating.toFixed(1)}
                </span>
              </div>
              <div className="flex items-center gap-1">
                {Array.from({ length: 5 }).map((_, index) => (
                  <Star
                    key={index}
                    className={cn(
                      "h-4 w-4",
                      index < Math.round(averageRating)
                        ? "fill-yellow-400 text-yellow-400"
                        : "text-muted-foreground/30"
                    )}
                  />
                ))}
              </div>
              <p className="text-sm text-muted-foreground">
                Based on {totalReviews.toLocaleString()} reviews
              </p>
            </div>

            {/* Rating Distribution */}
            <div className="flex-1">
              <RatingDistribution />
            </div>
          </div>
        </div>
      )}

      {/* Reviews List */}
      {reviews.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed bg-muted/30 py-16">
          <MessageSquare className="h-12 w-12 text-muted-foreground/50" />
          <h3 className="mt-3 text-lg font-semibold">No reviews yet</h3>
          <p className="text-sm text-muted-foreground">
            Be the first to share your thoughts on this book
          </p>
          {onWriteReview && (
            <Button onClick={onWriteReview} className="mt-4">
              Write a Review
            </Button>
          )}
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {displayedReviews.map((review) => (
              <ReviewCard
                key={review.id}
                review={review}
                onHelpful={onHelpful}
              />
            ))}
          </div>

          {/* Load More / Show All */}
          {shouldShowLoadMore && (
            <div className="flex flex-col items-center gap-3 pt-2">
              <Button
                variant="outline"
                onClick={handleLoadMore}
                className="group gap-2 transition-all hover:gap-3"
              >
                <span>Load More Reviews</span>
                <ChevronDown className="h-4 w-4 transition-transform group-hover:translate-y-0.5" />
              </Button>
              {visibleReviews > maxInitialDisplay && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span>Showing {visibleReviews} of {reviews.length}</span>
                  <div className="h-px w-8 bg-muted-foreground/20" />
                  <span>{Math.round((visibleReviews / reviews.length) * 100)}%</span>
                </div>
              )}
            </div>
          )}

          {expanded && reviews.length > maxInitialDisplay && (
            <div className="flex flex-col items-center gap-2 pt-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Sparkles className="h-4 w-4" />
                <span>All {reviews.length} reviews shown</span>
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
}