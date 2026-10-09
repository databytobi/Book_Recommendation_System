// apps/frontend/web/components/dashboard/Navbar.tsx

"use client";

import Link from "next/link";
// FIX: Removed unused 'usePathname' import
import { Menu, BookOpen } from "lucide-react"; // FIX: Removed unused 'Bell' import
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { SearchBar } from "./SearchBar";
import { UserMenu } from "./UserMenu";
import { NotificationMenu } from "./NotificationMenu";

interface NavbarProps {
  onMenuClick?: () => void;
  className?: string;
}

export function Navbar({ onMenuClick, className }: NavbarProps) {
  // FIX: Removed unused 'pathname' variable
  // const pathname = usePathname();

  return (
    <header
      className={cn(
        "sticky top-0 z-40 flex h-16 items-center justify-between border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-4 lg:px-6 transition-colors",
        className
      )}
    >
      {/* Left Section - Mobile menu + Logo */}
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          onClick={onMenuClick}
          className="lg:hidden h-9 w-9 rounded-md hover:bg-muted/60"
        >
          <Menu className="h-5 w-5" />
        </Button>

        {/* ONLY ONE Logo - in the navbar */}
        <Link href="/dashboard" className="hidden lg:flex items-center gap-2.5 group">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-600 to-violet-600 text-white shadow-sm">
            <BookOpen className="h-4 w-4" />
          </div>
          <span className="font-semibold text-foreground text-sm tracking-tight">
            BookRec
          </span>
        </Link>
      </div>

      {/* Center - Search (only ONE search bar) */}
      <div className="hidden md:flex flex-1 max-w-md mx-4">
        <SearchBar />
      </div>

      {/* Right Section - Theme, Notifications, User (each only once) */}
      <div className="flex items-center gap-1.5">
        <ThemeToggle />
        <NotificationMenu />
        <UserMenu />
      </div>
    </header>
  );
}