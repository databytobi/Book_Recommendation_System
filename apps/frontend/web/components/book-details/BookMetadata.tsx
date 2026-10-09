"use client";

import {
  Calendar,
  BookOpen,
  Globe,
  Building2,
  Hash,
  // FIX: Removed unused 'Clock' import
  Info,
  ChevronRight,
} from "lucide-react";

import { cn } from "@/lib/utils";

interface BookMetadataProps {
  isbn?: string;
  publisher?: string;
  language?: string;
  pages?: number;
  publicationDate?: string;
  // FIX: Removed readingTime
  className?: string;
  variant?: "grid" | "list" | "compact";
  showHeader?: boolean;
  onExpand?: () => void;
}

interface MetadataItemProps {
  icon: React.ReactNode;
  label: string;
  value?: string | number;
  className?: string;
  size?: "sm" | "default";
}

// FIX: Helper function to format publication date
function formatPublicationDate(dateString?: string): string | undefined {
  if (!dateString) return undefined;
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return dateString;
  }
}

function MetadataItem({
  icon,
  label,
  value,
  className,
  size = "default",
}: MetadataItemProps) {
  if (!value) return null;

  const iconSize = size === "sm" ? "h-4 w-4" : "h-5 w-5";
  const padding = size === "sm" ? "p-2" : "p-4";
  const iconPadding = size === "sm" ? "p-1.5" : "p-2";
  const valueSize = size === "sm" ? "text-sm" : "text-base";

  return (
    <div
      className={cn(
        "group flex items-start gap-3 rounded-xl border bg-card transition-all hover:shadow-md hover:shadow-primary/5",
        padding,
        className
      )}
    >
      <div
        className={cn(
          "rounded-lg bg-gradient-to-br from-primary/10 to-primary/5 text-primary transition-all group-hover:scale-105 group-hover:from-primary/20 group-hover:to-primary/10",
          iconPadding
        )}
      >
        <div className={iconSize}>{icon}</div>
      </div>

      <div className="flex-1 min-w-0">
        <p
          className={cn(
            "text-xs font-medium uppercase tracking-wider text-muted-foreground",
            size === "sm" && "text-[10px]"
          )}
        >
          {label}
        </p>
        <p
          className={cn(
            "mt-1 truncate font-medium text-foreground",
            valueSize
          )}
          title={typeof value === "string" ? value : undefined}
        >
          {value}
        </p>
      </div>
    </div>
  );
}

export function BookMetadata({
  isbn,
  publisher,
  language,
  pages,
  publicationDate,
  className,
  variant = "grid",
  showHeader = true,
  onExpand,
}: BookMetadataProps) {
  // FIX: Format publication date
  const formattedPublicationDate = formatPublicationDate(publicationDate);

  const metadataItems = [
    { icon: <Hash />, label: "ISBN", value: isbn },
    { icon: <Building2 />, label: "Publisher", value: publisher },
    { icon: <Globe />, label: "Language", value: language },
    { icon: <BookOpen />, label: "Pages", value: pages },
    // FIX: Use formatted date
    { icon: <Calendar />, label: "Publication Date", value: formattedPublicationDate },
    // FIX: Removed readingTime item
  ];

  const visibleItems = metadataItems.filter((item) => item.value);
  const hasItems = visibleItems.length > 0;

  if (!hasItems) {
    return (
      <div
        className={cn(
          "rounded-2xl border border-dashed bg-muted/30 p-8 text-center",
          className
        )}
      >
        <Info className="mx-auto h-10 w-10 text-muted-foreground/50" />
        <p className="mt-2 text-sm text-muted-foreground">No metadata available</p>
      </div>
    );
  }

  return (
    <section className={cn("space-y-5", className)}>
      {/* Header */}
      {showHeader && (
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-primary/10 p-1.5">
                <Info className="h-4 w-4 text-primary" />
              </div>
              <h2 className="text-xl font-semibold tracking-tight">Book Details</h2>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              Essential information about this book
            </p>
          </div>
          {onExpand && (
            <button
              onClick={onExpand}
              className="group inline-flex items-center gap-1 text-sm font-medium text-primary transition-all hover:gap-2"
            >
              <span>View All</span>
              <ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </button>
          )}
        </div>
      )}

      {/* Metadata Grid */}
      {variant === "compact" ? (
        <div className="flex flex-wrap gap-2">
          {visibleItems.map((item) => (
            <MetadataItem
              key={item.label}
              icon={item.icon}
              label={item.label}
              value={item.value}
              size="sm"
              className="flex-1 min-w-[140px]"
            />
          ))}
        </div>
      ) : variant === "list" ? (
        <div className="space-y-2">
          {visibleItems.map((item) => (
            <MetadataItem
              key={item.label}
              icon={item.icon}
              label={item.label}
              value={item.value}
              className="w-full"
            />
          ))}
        </div>
      ) : (
        <div
          className={cn(
            "grid gap-4",
            visibleItems.length === 1 && "grid-cols-1",
            visibleItems.length === 2 && "grid-cols-2",
            visibleItems.length >= 3 && "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"
          )}
        >
          {visibleItems.map((item) => (
            <MetadataItem
              key={item.label}
              icon={item.icon}
              label={item.label}
              value={item.value}
            />
          ))}
        </div>
      )}

      {/* FIX: Removed Sparkles decorative element */}
    </section>
  );
}