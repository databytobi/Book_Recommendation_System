"use client";

import { useState } from "react";
import {
  X,
  SlidersHorizontal,
  BookOpen,
  Globe,
  Star,
  ChevronDown,
  Filter,
  // FIX: Removed unused 'Sparkles'
  Check,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface FilterOption {
  label: string;
  value: string;
  count?: number;
}

interface SearchFiltersProps {
  genres: FilterOption[];
  languages: FilterOption[];
  ratings: FilterOption[];
  selectedGenre?: string;
  selectedLanguage?: string;
  selectedRating?: string;
  className?: string;
  onGenreChange?: (value: string) => void;
  onLanguageChange?: (value: string) => void;
  onRatingChange?: (value: string) => void;
  onClearFilters?: () => void;
  variant?: "default" | "compact" | "minimal";
  showCounts?: boolean;
  showActiveFilters?: boolean;
}

function FilterSelect({
  label,
  value,
  options,
  onChange,
  icon: Icon,
  placeholder,
  variant,
}: {
  label: string;
  value: string;
  options: FilterOption[];
  onChange: (value: string) => void;
  icon: React.ElementType;
  placeholder: string;
  variant?: "default" | "compact" | "minimal";
}) {
  const [isOpen, setIsOpen] = useState(false);
  const isCompact = variant === "compact";
  const isMinimal = variant === "minimal";

  const selectedOption = options.find((opt) => opt.value === value);

  return (
    <div className="relative">
      {/* Label */}
      {!isMinimal && (
        <label className="mb-1.5 block text-xs font-medium text-muted-foreground">
          {label}
        </label>
      )}

      {/* Select Trigger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "group flex w-full items-center gap-2 rounded-xl border bg-background transition-all duration-200 hover:border-primary/50 hover:shadow-md",
          isCompact ? "h-9 px-3 text-sm" : "h-11 px-4 text-sm",
          isMinimal && "border-0 bg-transparent px-2 hover:bg-primary/5",
          isOpen && "border-primary ring-2 ring-primary/20"
        )}
      >
        <Icon className={cn(
          "text-muted-foreground transition-colors group-hover:text-primary",
          isCompact ? "h-4 w-4" : "h-4 w-4"
        )} />

        <span className={cn(
          "flex-1 truncate text-left",
          !selectedOption && "text-muted-foreground"
        )}>
          {selectedOption?.label || placeholder}
        </span>

        {!isMinimal && (
          <ChevronDown className={cn(
            "h-4 w-4 text-muted-foreground transition-transform duration-200",
            isOpen && "rotate-180"
          )} />
        )}
      </button>

      {/* Options Dropdown */}
      {isOpen && !isMinimal && (
        <div className="absolute left-0 right-0 top-full z-50 mt-1 max-h-60 overflow-auto rounded-xl border bg-popover p-1 shadow-lg">
          {/* Clear option */}
          <button
            onClick={() => {
              onChange("");
              setIsOpen(false);
            }}
            className={cn(
              "flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-primary/10 hover:text-primary",
              !value && "bg-primary/10 text-primary"
            )}
          >
            <span>All {label}s</span>
            {!value && <Check className="ml-auto h-4 w-4" />}
          </button>

          {options.map((option) => {
            const isSelected = value === option.value;
            return (
              <button
                key={option.value}
                onClick={() => {
                  onChange(option.value);
                  setIsOpen(false);
                }}
                className={cn(
                  "flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-primary/10",
                  isSelected && "bg-primary/10 text-primary"
                )}
              >
                <span className="flex-1 truncate">{option.label}</span>
                {option.count !== undefined && (
                  <span className="text-xs text-muted-foreground">
                    {option.count}
                  </span>
                )}
                {isSelected && <Check className="h-4 w-4" />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

function ActiveFilterBadge({
  label,
  value,
  onRemove,
}: {
  label: string;
  value: string;
  onRemove: () => void;
}) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary transition-all hover:bg-primary/20">
      <span>{label}: {value}</span>
      <button
        onClick={onRemove}
        className="rounded-full p-0.5 transition-colors hover:bg-primary/20"
      >
        <X className="h-3 w-3" />
      </button>
    </span>
  );
}

export function SearchFilters({
  genres,
  languages,
  ratings,
  selectedGenre = "",
  selectedLanguage = "",
  selectedRating = "",
  className,
  onGenreChange,
  onLanguageChange,
  onRatingChange,
  onClearFilters,
  variant = "default",
  // FIX: Removed unused 'showCounts' entirely
  showActiveFilters = true,
}: SearchFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const isCompact = variant === "compact";
  const isMinimal = variant === "minimal";

  const hasFilters = selectedGenre || selectedLanguage || selectedRating;

  const getLabelForValue = (options: FilterOption[], value: string) => {
    return options.find((opt) => opt.value === value)?.label || value;
  };

  return (
    <section
      className={cn(
        "relative",
        !isMinimal && "rounded-2xl border bg-card p-5 transition-all hover:shadow-md",
        isCompact && "p-3",
        isMinimal && "border-0 bg-transparent p-0 shadow-none",
        className
      )}
    >
      {/* Decorative background */}
      {!isMinimal && (
        <div className="absolute inset-0 -z-10 overflow-hidden rounded-2xl">
          <div className="absolute -right-20 -top-20 h-40 w-40 rounded-full bg-primary/5 blur-2xl" />
          <div className="absolute -bottom-20 -left-20 h-40 w-40 rounded-full bg-secondary/5 blur-2xl" />
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {!isMinimal && (
            <div className="rounded-lg bg-primary/10 p-1.5">
              <SlidersHorizontal className="h-4 w-4 text-primary" />
            </div>
          )}
          <h3 className={cn(
            "font-semibold tracking-tight",
            isCompact ? "text-base" : "text-lg",
            isMinimal && "text-sm"
          )}>
            Filters
          </h3>
          {hasFilters && !isMinimal && (
            <span className="rounded-full bg-primary px-2 py-0.5 text-xs font-medium text-primary-foreground">
              {[selectedGenre, selectedLanguage, selectedRating].filter(Boolean).length}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {!isMinimal && hasFilters && (
            <Button
              variant="ghost"
              size={isCompact ? "sm" : "sm"}
              onClick={onClearFilters}
              className="gap-1 text-muted-foreground transition-all hover:gap-2 hover:text-destructive"
            >
              <X className="h-4 w-4" />
              <span className={cn(isCompact ? "hidden sm:inline" : "inline")}>
                Clear All
              </span>
            </Button>
          )}

          {!isMinimal && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-muted-foreground"
            >
              <ChevronDown className={cn(
                "h-4 w-4 transition-transform duration-200",
                !isExpanded && "-rotate-90"
              )} />
            </Button>
          )}
        </div>
      </div>

      {/* Active Filters */}
      {showActiveFilters && hasFilters && !isMinimal && (
        <div className="mt-3 flex flex-wrap gap-1.5 border-t border-border/50 pt-3">
          {selectedGenre && onGenreChange && (
            <ActiveFilterBadge
              label="Genre"
              value={getLabelForValue(genres, selectedGenre)}
              onRemove={() => onGenreChange("")}
            />
          )}
          {selectedLanguage && onLanguageChange && (
            <ActiveFilterBadge
              label="Language"
              value={getLabelForValue(languages, selectedLanguage)}
              onRemove={() => onLanguageChange("")}
            />
          )}
          {selectedRating && onRatingChange && (
            <ActiveFilterBadge
              label="Rating"
              value={getLabelForValue(ratings, selectedRating)}
              onRemove={() => onRatingChange("")}
            />
          )}
        </div>
      )}

      {/* Filter Controls */}
      <div className={cn(
        "grid gap-4 transition-all duration-300",
        isExpanded ? "mt-4 opacity-100" : "max-h-0 overflow-hidden opacity-0",
        isCompact ? "grid-cols-1 sm:grid-cols-3" : "grid-cols-1 md:grid-cols-3",
        isMinimal && "grid-cols-1 sm:grid-cols-3"
      )}>
        {/* Genre */}
        <FilterSelect
          label="Genre"
          value={selectedGenre}
          options={genres}
          onChange={onGenreChange || (() => {})}
          icon={BookOpen}
          placeholder="All Genres"
          variant={variant}
        />

        {/* Language */}
        <FilterSelect
          label="Language"
          value={selectedLanguage}
          options={languages}
          onChange={onLanguageChange || (() => {})}
          icon={Globe}
          placeholder="All Languages"
          variant={variant}
        />

        {/* Rating */}
        <FilterSelect
          label="Rating"
          value={selectedRating}
          options={ratings}
          onChange={onRatingChange || (() => {})}
          icon={Star}
          placeholder="Any Rating"
          variant={variant}
        />
      </div>

      {/* Decorative footer for default variant */}
      {!isMinimal && !isCompact && (
        <div className="mt-4 flex items-center gap-2">
          <div className="h-px flex-1 bg-gradient-to-r from-primary/10 to-transparent" />
          <div className="flex items-center gap-1 text-[10px] text-muted-foreground/50">
            <Filter className="h-3 w-3" />
            <span>{hasFilters ? "Filters active" : "Refine your search"}</span>
          </div>
          <div className="h-px flex-1 bg-gradient-to-l from-primary/10 to-transparent" />
        </div>
      )}
    </section>
  );
}