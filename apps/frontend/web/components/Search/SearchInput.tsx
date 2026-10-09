"use client";

import { 
  Search, 
  X, 
  Loader2, 
  Sparkles,
  Command,
  Mic,
  ArrowRight,
} from "lucide-react";
import { ChangeEvent, useState, useRef, useEffect } from "react";

import { cn } from "@/lib/utils";

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  loading?: boolean;
  disabled?: boolean;
  autoFocus?: boolean;
  className?: string;
  onClear?: () => void;
  onFocus?: () => void;
  onBlur?: () => void;
  onSubmit?: (value: string) => void;
  variant?: "default" | "minimal" | "rounded";
  size?: "sm" | "default" | "lg";
  showShortcut?: boolean;
  showVoiceSearch?: boolean;
  onVoiceSearch?: () => void;
  suggestions?: string[];
  onSuggestionClick?: (suggestion: string) => void;
}

export function SearchInput({
  value,
  onChange,
  placeholder = "Search books, authors, ISBN...",
  loading = false,
  disabled = false,
  autoFocus = false,
  className,
  onClear,
  onFocus,
  onBlur,
  onSubmit,
  variant = "default",
  size = "default",
  showShortcut = true,
  showVoiceSearch = false,
  onVoiceSearch,
  suggestions = [],
  onSuggestionClick,
}: SearchInputProps) {
  const [isFocused, setIsFocused] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [autoFocus]);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
    if (e.target.value.length > 0) {
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  };

  const handleClear = () => {
    onChange("");
    setShowSuggestions(false);
    onClear?.();
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && onSubmit) {
      onSubmit(value);
      setShowSuggestions(false);
    }
    if (e.key === "Escape") {
      setShowSuggestions(false);
      if (inputRef.current) {
        inputRef.current.blur();
      }
    }
  };

  const handleFocus = () => {
    setIsFocused(true);
    onFocus?.();
    if (value.length > 0) {
      setShowSuggestions(true);
    }
  };

  const handleBlur = () => {
    // Delay hiding suggestions to allow click on suggestion
    setTimeout(() => {
      setIsFocused(false);
      setShowSuggestions(false);
      onBlur?.();
    }, 200);
  };

  const handleSuggestionClick = (suggestion: string) => {
    onChange(suggestion);
    setShowSuggestions(false);
    onSuggestionClick?.(suggestion);
    if (onSubmit) {
      onSubmit(suggestion);
    }
  };

  // Size configurations
  const sizeConfig = {
    sm: {
      height: "h-10",
      paddingLeft: "pl-9",
      paddingRight: "pr-9",
      iconSize: "h-4 w-4",
      textSize: "text-sm",
      fontSize: "text-sm",
    },
    default: {
      height: "h-12",
      paddingLeft: "pl-11",
      paddingRight: "pr-11",
      iconSize: "h-5 w-5",
      textSize: "text-base",
      fontSize: "text-sm",
    },
    lg: {
      height: "h-14",
      paddingLeft: "pl-12",
      paddingRight: "pr-12",
      iconSize: "h-5 w-5",
      textSize: "text-lg",
      fontSize: "text-base",
    },
  };

  const styles = sizeConfig[size];

  // Variant configurations
  const variantClasses = {
    default: cn(
      "border bg-background",
      "focus:border-primary focus:ring-2 focus:ring-primary/20",
      "hover:border-primary/50 hover:shadow-md"
    ),
    minimal: cn(
      "border-0 bg-transparent shadow-none",
      "focus:border-b-2 focus:border-primary focus:ring-0",
      "rounded-none border-b border-border"
    ),
    rounded: cn(
      "border bg-background",
      "rounded-full",
      "focus:border-primary focus:ring-2 focus:ring-primary/20",
      "hover:border-primary/50 hover:shadow-lg"
    ),
  };

  return (
    <div className={cn("relative w-full", className)}>
      {/* Input Container */}
      <div
        className={cn(
          "relative flex items-center transition-all duration-300",
          variantClasses[variant],
          styles.height,
          disabled && "cursor-not-allowed opacity-50",
          variant === "rounded" && "rounded-full",
          variant === "default" && "rounded-xl"
        )}
      >
        {/* Left Icon */}
        <div className="absolute left-3 flex items-center">
          <Search
            className={cn(
              styles.iconSize,
              "text-muted-foreground transition-colors",
              isFocused && "text-primary"
            )}
          />
        </div>

        {/* Input */}
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={placeholder}
          disabled={disabled}
          className={cn(
            "h-full w-full bg-transparent outline-none transition-colors",
            styles.paddingLeft,
            styles.paddingRight,
            styles.fontSize,
            "placeholder:text-muted-foreground/70",
            disabled && "cursor-not-allowed",
            variant === "minimal" && "pl-0"
          )}
        />

        {/* Right Side */}
        <div className="absolute right-3 flex items-center gap-1.5">
          {/* Voice Search */}
          {showVoiceSearch && !loading && (
            <button
              type="button"
              onClick={onVoiceSearch}
              className={cn(
                "rounded-full p-1.5 transition-all hover:bg-primary/10 hover:text-primary",
                "text-muted-foreground"
              )}
              aria-label="Voice search"
            >
              <Mic className={cn(styles.iconSize, "h-4 w-4")} />
            </button>
          )}

          {/* Loading */}
          {loading ? (
            <Loader2
              className={cn(
                styles.iconSize,
                "animate-spin text-primary"
              )}
            />
          ) : (
            // Clear Button
            value.length > 0 && (
              <button
                type="button"
                onClick={handleClear}
                className={cn(
                  "rounded-full p-1 transition-all duration-200",
                  "text-muted-foreground hover:bg-primary/10 hover:text-primary",
                  "hover:scale-110 active:scale-90"
                )}
                aria-label="Clear search"
              >
                <X className={cn(styles.iconSize, "h-4 w-4")} />
              </button>
            )
          )}

          {/* Keyboard Shortcut */}
          {showShortcut && !loading && !value && (
            <kbd
              className={cn(
                "hidden items-center gap-0.5 rounded-md border bg-muted/50 px-1.5 py-0.5 font-mono text-xs text-muted-foreground",
                "sm:flex"
              )}
            >
              <Command className="h-3 w-3" />
              <span>K</span>
            </kbd>
          )}
        </div>
      </div>

      {/* Suggestions Dropdown */}
      {showSuggestions && suggestions.length > 0 && value.length > 0 && (
        <div className="absolute left-0 right-0 top-full z-50 mt-1 max-h-60 overflow-auto rounded-xl border bg-popover p-1 shadow-lg">
          <div className="px-2 py-1.5 text-xs font-medium text-muted-foreground">
            Suggestions
          </div>
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => handleSuggestionClick(suggestion)}
              className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-primary/10"
            >
              <Search className="h-3.5 w-3.5 text-muted-foreground" />
              <span className="flex-1 text-left">{suggestion}</span>
              <ArrowRight className="h-3.5 w-3.5 text-muted-foreground/50" />
            </button>
          ))}
        </div>
      )}

      {/* Character Count */}
      {value.length > 0 && !loading && (
        <div className="absolute -bottom-5 right-0 text-[10px] text-muted-foreground/50">
          {value.length} characters
        </div>
      )}

      {/* Decorative Sparkle - appears on focus */}
      {isFocused && !loading && variant === "default" && (
        <div className="absolute -right-1 -top-1">
          <Sparkles className="h-3 w-3 animate-pulse text-primary" />
        </div>
      )}
    </div>
  );
}