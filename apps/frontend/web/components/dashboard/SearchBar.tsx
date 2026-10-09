// apps/frontend/web/components/layout/SearchBar.tsx

"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Search, X, Loader2, Command, FileText, User, BookOpen } from "lucide-react";
import { cn } from "@/lib/utils";
// FIX: Removed unused 'Button' import
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

// Step 1: Added real API import
import { apiClient } from "@/lib/api/client";

interface SearchBarProps {
  className?: string;
  placeholder?: string;
  onSearch?: (query: string) => void;
}

// Step 2: Replaced SearchResult interface
interface SearchResult {
  id: string;
  title: string;
  subtitle?: string;
  type: "book";
  url: string;
}

interface BookSearchResponse {
  results: {
    isbn: string;
    title: string;
    authors: string[];
  }[];
  total: number;
}

// Step 1: Removed mockSearchData entirely

const getIconForType = (type: SearchResult["type"]) => {
  switch (type) {
    case "book":
      return <BookOpen className="h-4 w-4" />;
    default:
      return <Search className="h-4 w-4" />;
  }
};

export function SearchBar({ className, placeholder = "Search books...", onSearch }: SearchBarProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Keyboard shortcut: Cmd+K or Ctrl+K to open search
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsOpen(true);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  // Click outside to close
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsFocused(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Step 3: Replaced performSearch with real API
  const performSearch = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setIsLoading(true);

    try {
      const response = await apiClient.get<BookSearchResponse>(
        `/books/search?q=${encodeURIComponent(searchQuery)}&limit=8`
      );

      const mapped: SearchResult[] = response.results.map((book) => ({
        id: book.isbn,
        title: book.title,
        subtitle: book.authors.join(", "),
        type: "book",
        url: `/dashboard/search?q=${encodeURIComponent(book.title)}`,
      }));

      setResults(mapped);
    } catch (error) {
      console.error("Search failed:", error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (query) {
        performSearch(query);
      } else {
        setResults([]);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query, performSearch]);

  // Step 4: handleSubmit kept exactly as specified
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!query.trim()) return;

    setIsOpen(false);
    setIsFocused(false);

    router.push(
      `/dashboard/search?q=${encodeURIComponent(query)}`
    );
  };

  const handleClear = () => {
    setQuery("");
    setResults([]);
    inputRef.current?.focus();
  };

  const handleSelect = (result: SearchResult) => {
    setIsOpen(false);
    setQuery("");
    setResults([]);
    router.push(result.url);
  };

  return (
    <>
      {/* Desktop Search Bar */}
      <div ref={containerRef} className={cn("relative hidden md:block", className)}>
        <form onSubmit={handleSubmit}>
          <div
            className={cn(
              "flex items-center rounded-lg border border-input bg-background transition-all duration-200",
              isFocused && "ring-2 ring-ring ring-offset-2"
            )}
          >
            <Search className="absolute left-3 h-4 w-4 text-muted-foreground pointer-events-none" />
            
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder={placeholder}
              className="flex h-10 w-72 rounded-lg bg-transparent pl-9 pr-8 py-2 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
              aria-label="Search"
              aria-describedby="search-description"
            />
            
            {query && (
              <button
                type="button"
                onClick={handleClear}
                className="absolute right-3 rounded-sm p-1 hover:bg-muted transition-colors"
                aria-label="Clear search"
              >
                <X className="h-3.5 w-3.5 text-muted-foreground" />
              </button>
            )}

            {/* Keyboard shortcut hint - Updated tooltip text */}
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger className="absolute right-3 hidden items-center gap-0.5 rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground pointer-events-none">
                  <Command className="h-3 w-3" />
                  <span>K</span>
                </TooltipTrigger>
                <TooltipContent>Press Ctrl+K (or Cmd+K on Mac)</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </form>

        {/* Search Results Dropdown */}
        {isFocused && query && (
          <div className="absolute top-full left-0 right-0 mt-2 rounded-lg border border-border bg-popover shadow-lg overflow-hidden z-50 animate-in slide-in-from-top-2">
            <div className="max-h-[300px] overflow-y-auto">
              {isLoading ? (
                <div className="flex items-center justify-center gap-2 py-8">
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Searching...</span>
                </div>
              ) : results.length > 0 ? (
                <div className="py-2">
                  {results.map((result) => (
                    <button
                      key={result.id}
                      onClick={() => handleSelect(result)}
                      className="flex w-full items-center gap-3 px-4 py-2.5 text-sm hover:bg-muted/50 transition-colors text-left"
                    >
                      <div className="flex h-8 w-8 items-center justify-center rounded-md bg-muted/50 text-muted-foreground">
                        {getIconForType(result.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{result.title}</p>
                        {result.subtitle && (
                          <p className="text-xs text-muted-foreground truncate">{result.subtitle}</p>
                        )}
                      </div>
                      <span className="text-xs text-muted-foreground capitalize">
                        {result.type}
                      </span>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center gap-1 py-8 text-sm text-muted-foreground">
                  <Search className="h-8 w-8 mb-2 text-muted-foreground/40" />
                  <p>No results found</p>
                  <p className="text-xs">Try adjusting your search</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Command Dialog (for Cmd+K) */}
      <CommandDialog open={isOpen} onOpenChange={setIsOpen}>
        <CommandInput
          placeholder="Search for books..."
          value={query}
          onValueChange={setQuery}
          onKeyDown={(e) => {
            if (e.key === "Enter" && query) {
              handleSubmit(e as unknown as React.FormEvent);
            }
          }}
        />
        <CommandList>
          {isLoading ? (
            <div className="flex items-center justify-center gap-2 py-12">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Searching...</span>
            </div>
          ) : (
            <>
              <CommandEmpty>
                <div className="flex flex-col items-center justify-center gap-1 py-8">
                  <Search className="h-10 w-10 text-muted-foreground/40" />
                  <p className="text-sm text-muted-foreground">No results found</p>
                  <p className="text-xs text-muted-foreground">Try a different search term</p>
                </div>
              </CommandEmpty>
              
              {results.length > 0 && (
                <>
                  <CommandGroup heading="Results">
                    {results.map((result) => (
                      <CommandItem
                        key={result.id}
                        onSelect={() => handleSelect(result)}
                        className="flex items-center gap-3 cursor-pointer"
                      >
                        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-muted/50 text-muted-foreground">
                          {getIconForType(result.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{result.title}</p>
                          {result.subtitle && (
                            <p className="text-xs text-muted-foreground truncate">{result.subtitle}</p>
                          )}
                        </div>
                        <span className="text-xs text-muted-foreground capitalize">
                          {result.type}
                        </span>
                      </CommandItem>
                    ))}
                  </CommandGroup>
                  
                  <CommandSeparator />
                  
                  <CommandGroup heading="Actions">
                    <CommandItem 
                      onSelect={() => handleSubmit({ preventDefault: () => {}, target: { query } } as unknown as React.FormEvent)}
                      className="cursor-pointer"
                    >
                      <Search className="mr-2 h-4 w-4" />
                      Search for &quot;{query}&quot;
                    </CommandItem>
                  </CommandGroup>
                </>
              )}
            </>
          )}
        </CommandList>
      </CommandDialog>
    </>
  );
}