// apps/frontend/web/components/books/BookSkeleton.tsx

import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface BookSkeletonProps {
  variant?: "default" | "compact" | "grid" | "list" | "featured";
  showActions?: boolean;
  showRating?: boolean;
  showTags?: boolean;
  count?: number;
  className?: string;
  animate?: boolean;
}

export function BookSkeleton({
  variant = "default",
  showActions = true,
  showRating = true,
  showTags = true,
  count = 1,
  className,
  animate = true,
}: BookSkeletonProps) {
  // Default skeleton
  const DefaultSkeleton = () => (
    <div className={cn(
      "overflow-hidden rounded-2xl border border-border/50 bg-card",
      "transition-all duration-300",
      animate && "animate-pulse",
      className
    )}>
      {/* Cover Image */}
      <div className="relative aspect-[2/3] w-full overflow-hidden bg-muted/50">
        <Skeleton className="h-full w-full rounded-none" />
        {/* Book spine shadow effect */}
        <div className="absolute inset-y-0 left-0 w-8 bg-gradient-to-r from-black/10 to-transparent" />
      </div>

      {/* Content */}
      <div className="space-y-3 p-4">
        {/* Title */}
        <Skeleton className="h-5 w-5/6" />
        
        {/* Author */}
        <Skeleton className="h-4 w-1/2" />
        
        {/* Rating */}
        {showRating && (
          <div className="flex items-center gap-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-12" />
          </div>
        )}
        
        {/* Tags */}
        {showTags && (
          <div className="flex flex-wrap gap-2">
            <Skeleton className="h-6 w-16 rounded-full" />
            <Skeleton className="h-6 w-20 rounded-full" />
            <Skeleton className="h-6 w-14 rounded-full" />
          </div>
        )}
        
        {/* Actions */}
        {showActions && (
          <div className="flex justify-between pt-2 border-t border-border/30">
            <Skeleton className="h-9 w-9 rounded-lg" />
            <Skeleton className="h-9 w-9 rounded-lg" />
            <Skeleton className="h-9 w-9 rounded-lg" />
            <Skeleton className="h-9 w-9 rounded-lg" />
          </div>
        )}
      </div>
    </div>
  );

  // Compact skeleton (smaller, for sidebars or lists)
  const CompactSkeleton = () => (
    <div className={cn(
      "flex gap-4 overflow-hidden rounded-xl border border-border/50 bg-card p-3",
      animate && "animate-pulse",
      className
    )}>
      <Skeleton className="h-24 w-16 rounded-lg shrink-0" />
      <div className="flex-1 space-y-2 py-1">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-3 w-1/2" />
        <div className="flex items-center gap-2">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-3 w-12" />
        </div>
        {showActions && (
          <div className="flex gap-2 pt-1">
            <Skeleton className="h-7 w-7 rounded-md" />
            <Skeleton className="h-7 w-7 rounded-md" />
          </div>
        )}
      </div>
    </div>
  );

  // Grid skeleton (for grid layouts)
  const GridSkeleton = () => (
    <div className={cn(
      "overflow-hidden rounded-xl border border-border/50 bg-card",
      animate && "animate-pulse",
      className
    )}>
      <Skeleton className="aspect-[2/3] w-full rounded-none" />
      <div className="space-y-2 p-3">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-3 w-1/2" />
        {showRating && (
          <div className="flex items-center gap-2">
            <Skeleton className="h-3 w-16" />
            <Skeleton className="h-3 w-10" />
          </div>
        )}
      </div>
    </div>
  );

  // List skeleton (horizontal, for lists)
  const ListSkeleton = () => (
    <div className={cn(
      "flex gap-4 overflow-hidden rounded-xl border border-border/50 bg-card p-4",
      animate && "animate-pulse",
      className
    )}>
      <Skeleton className="h-32 w-24 rounded-lg shrink-0" />
      <div className="flex-1 space-y-2 py-1">
        <Skeleton className="h-5 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
        {showRating && (
          <div className="flex items-center gap-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-12" />
          </div>
        )}
        {showTags && (
          <div className="flex flex-wrap gap-2 pt-1">
            <Skeleton className="h-5 w-16 rounded-full" />
            <Skeleton className="h-5 w-20 rounded-full" />
          </div>
        )}
        {showActions && (
          <div className="flex gap-2 pt-2">
            <Skeleton className="h-8 w-8 rounded-md" />
            <Skeleton className="h-8 w-8 rounded-md" />
            <Skeleton className="h-8 w-8 rounded-md" />
          </div>
        )}
      </div>
    </div>
  );

  // Featured skeleton (large, for featured books)
  const FeaturedSkeleton = () => (
    <div className={cn(
      "relative overflow-hidden rounded-2xl border border-border/50 bg-card",
      animate && "animate-pulse",
      className
    )}>
      <div className="flex flex-col md:flex-row">
        <Skeleton className="aspect-[2/3] md:aspect-auto md:h-64 md:w-48 shrink-0" />
        <div className="flex-1 space-y-4 p-6">
          <Skeleton className="h-8 w-2/3" />
          <Skeleton className="h-5 w-1/3" />
          <div className="flex items-center gap-3">
            <Skeleton className="h-5 w-24" />
            <Skeleton className="h-5 w-16" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/6" />
          </div>
          {showTags && (
            <div className="flex flex-wrap gap-2">
              <Skeleton className="h-6 w-20 rounded-full" />
              <Skeleton className="h-6 w-24 rounded-full" />
              <Skeleton className="h-6 w-16 rounded-full" />
            </div>
          )}
          {showActions && (
            <div className="flex gap-3 pt-2">
              <Skeleton className="h-10 w-32 rounded-md" />
              <Skeleton className="h-10 w-10 rounded-md" />
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // Render based on variant
  const getSkeleton = () => {
    switch (variant) {
      case "compact":
        return <CompactSkeleton />;
      case "grid":
        return <GridSkeleton />;
      case "list":
        return <ListSkeleton />;
      case "featured":
        return <FeaturedSkeleton />;
      default:
        return <DefaultSkeleton />;
    }
  };

  // Render multiple skeletons if count > 1
  if (count > 1) {
    return (
      <div className={cn(
        "grid gap-4",
        variant === "list" ? "grid-cols-1" : "grid-cols-2 sm:grid-cols-3 lg:grid-cols-4"
      )}>
        {Array.from({ length: count }).map((_, index) => (
          <div key={index}>{getSkeleton()}</div>
        ))}
      </div>
    );
  }

  return getSkeleton();
}

// ============================================================
// Pre-configured variants for common use cases
// ============================================================

export function BookSkeletonGrid({ count = 8, className }: { count?: number; className?: string }) {
  return (
    <BookSkeleton 
      variant="grid" 
      count={count} 
      className={className}
      showActions={false}
      showRating={true}
      showTags={false}
    />
  );
}

export function BookSkeletonList({ count = 5, className }: { count?: number; className?: string }) {
  return (
    <BookSkeleton 
      variant="list" 
      count={count} 
      className={className}
      showActions={true}
      showRating={true}
      showTags={true}
    />
  );
}

export function BookSkeletonFeatured({ className }: { className?: string }) {
  return (
    <BookSkeleton 
      variant="featured" 
      className={className}
      showActions={true}
      showRating={true}
      showTags={true}
    />
  );
}

export function BookSkeletonCompact({ count = 3, className }: { count?: number; className?: string }) {
  return (
    <BookSkeleton 
      variant="compact" 
      count={count} 
      className={className}
      showActions={false}
      showRating={true}
      showTags={false}
    />
  );
}