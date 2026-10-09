"use client";

import Image from "next/image";
import { ArrowRight, BookOpen, User, Users } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface AuthorSectionProps {
  name: string;
  biography?: string;
  imageUrl?: string;
  booksPublished?: number;
  followers?: number;
  onViewProfile?: () => void;
  // FIX: Added onBrowseBooks callback
  onBrowseBooks?: () => void;
  className?: string;
  bookGenres?: string[];
  // FIX: Removed joinDate - it has no real purpose
}

export function AuthorSection({
  name,
  biography,
  imageUrl,
  booksPublished,
  followers,
  onViewProfile,
  onBrowseBooks,
  className,
  bookGenres,
}: AuthorSectionProps) {
  return (
    <section
      className={cn(
        "group rounded-2xl border bg-card p-6 transition-all hover:shadow-lg hover:shadow-primary/5",
        className
      )}
    >
      <div className="flex flex-col gap-6 md:flex-row md:items-start">
        {/* Avatar with decorative ring */}
        <div className="flex-shrink-0">
          <div className="relative">
            {/* Decorative ring */}
            <div className="absolute -inset-1 rounded-full bg-gradient-to-br from-primary/20 to-primary/5 blur-md transition-opacity group-hover:opacity-100 md:opacity-0" />
            
            {imageUrl ? (
              <Image
                src={imageUrl}
                alt={name}
                width={96}
                height={96}
                className="relative rounded-full object-cover ring-2 ring-border transition-all group-hover:ring-primary/50"
              />
            ) : (
              <div className="relative flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-primary/10 to-primary/5 text-3xl font-bold text-primary ring-2 ring-border transition-all group-hover:ring-primary/50">
                {/* FIX: Improved name.charAt(0) */}
                {name.trim().charAt(0).toUpperCase()}
              </div>
            )}
          </div>
        </div>

        {/* Information */}
        <div className="flex-1 space-y-4">
          {/* Header */}
          <div>
            <div className="flex items-center gap-2">
              <User className="h-3.5 w-3.5 text-muted-foreground" />
              <p className="text-sm font-medium text-muted-foreground">
                Author
              </p>
            </div>

            <h2 className="mt-1 text-3xl font-bold tracking-tight transition-colors group-hover:text-primary">
              {name}
            </h2>
          </div>

          {/* Biography with gradient fade for long text */}
          {biography && (
            <div className="relative max-h-24 overflow-hidden">
              <p className="leading-relaxed text-muted-foreground">
                {biography}
              </p>
              {biography.length > 200 && (
                <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-card to-transparent" />
              )}
            </div>
          )}

          {/* Stats with icons */}
          <div className="flex flex-wrap gap-6">
            {booksPublished !== undefined && (
              <div className="flex items-center gap-2 rounded-lg bg-secondary/50 px-3 py-1.5 transition-colors hover:bg-secondary">
                <BookOpen className="h-4 w-4 text-primary" />
                <div>
                  <span className="font-semibold text-foreground">
                    {booksPublished}
                  </span>
                  <span className="ml-1 text-sm text-muted-foreground">
                    {booksPublished === 1 ? "Book" : "Books"}
                  </span>
                </div>
              </div>
            )}

            {followers !== undefined && (
              <div className="flex items-center gap-2 rounded-lg bg-secondary/50 px-3 py-1.5 transition-colors hover:bg-secondary">
                <Users className="h-4 w-4 text-primary" />
                <div>
                  <span className="font-semibold text-foreground">
                    {followers >= 1000
                      ? `${(followers / 1000).toFixed(1)}K`
                      : followers.toLocaleString()}
                  </span>
                  <span className="ml-1 text-sm text-muted-foreground">
                    Followers
                  </span>
                </div>
              </div>
            )}

            {bookGenres && bookGenres.length > 0 && (
              <div className="flex items-center gap-2 rounded-lg bg-secondary/50 px-3 py-1.5">
                <span className="text-xs font-medium text-muted-foreground">
                  {bookGenres.slice(0, 3).join(" • ")}
                  {bookGenres.length > 3 && ` +${bookGenres.length - 3}`}
                </span>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-3 pt-1">
            <Button
              onClick={onViewProfile}
              className="group/btn transition-all hover:gap-2"
            >
              View Author Profile
              <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover/btn:translate-x-1" />
            </Button>
            
            {booksPublished !== undefined && booksPublished > 0 && (
              <Button 
                variant="ghost" 
                size="sm" 
                className="text-muted-foreground"
                // FIX: Made Browse Books functional
                onClick={onBrowseBooks}
              >
                Browse Books
              </Button>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}