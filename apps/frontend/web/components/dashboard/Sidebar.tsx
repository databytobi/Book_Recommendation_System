// apps/frontend/web/components/dashboard/Sidebar.tsx

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Compass,
  Sparkles,
  Search,
  Library,
  Heart,
  History,
  User,
  Settings,
  // FIX: Removed unused 'BookOpen' import
  LogOut,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
// FIX: Removed unused Avatar imports
import { ThemeToggle } from "@/components/ui/theme-toggle";

// Navigation items (simplified)
const navigationItems = [
  { title: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { title: "Discover", href: "/dashboard/discover", icon: Compass },
  { title: "Recommendations", href: "/dashboard/recommendations", icon: Sparkles },
  { title: "Search", href: "/dashboard/search", icon: Search },
  { title: "Library", href: "/dashboard/library", icon: Library },
  { title: "Favorites", href: "/dashboard/favorites", icon: Heart },
  { title: "Reading History", href: "/dashboard/history", icon: History },
];

const accountItems = [
  { title: "Profile", href: "/dashboard/profile", icon: User },
  { title: "Settings", href: "/dashboard/settings", icon: Settings },
];

interface SidebarProps {
  isCollapsed?: boolean;
  onToggle?: () => void;
  className?: string;
}

export function Sidebar({ isCollapsed = false, onToggle, className }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "sticky top-0 z-40 flex h-screen flex-col border-r border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 transition-all duration-300 ease-in-out",
        isCollapsed ? "w-[72px]" : "w-72",
        className
      )}
    >
      {/* REMOVED: Logo Section - BookRec is now only in Navbar */}
      {/* The entire div with "BookRec" has been removed */}
      
      {/* Toggle Button Only - Moved to top */}
      <div className="flex h-16 items-center justify-end border-b border-border/40 px-4 shrink-0">
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className="h-7 w-7 rounded-md hover:bg-muted/60 shrink-0"
        >
          {isCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        <div className={cn("mb-2", isCollapsed && "sr-only")}>
          <p className="px-3 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
            Navigation
          </p>
        </div>

        <div className="space-y-0.5">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-muted/50 hover:text-foreground",
                  isCollapsed && "justify-center px-0"
                )}
              >
                <Icon className={cn("h-5 w-5 shrink-0", isActive && "text-primary")} />
                {!isCollapsed && <span className="flex-1 truncate">{item.title}</span>}
              </Link>
            );
          })}
        </div>

        <div className="my-6 border-t border-border/40" />

        <div className={cn("mb-2", isCollapsed && "sr-only")}>
          <p className="px-3 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
            Account
          </p>
        </div>

        <div className="space-y-0.5">
          {accountItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-muted/50 hover:text-foreground",
                  isCollapsed && "justify-center px-0"
                )}
              >
                <Icon className={cn("h-5 w-5 shrink-0", isActive && "text-primary")} />
                {!isCollapsed && <span className="flex-1 truncate">{item.title}</span>}
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Bottom Section */}
      <div className="shrink-0 border-t border-border/40 p-4 space-y-3">
        <div className="flex items-center justify-between gap-2">
          <ThemeToggle />
          <Button
            variant="ghost"
            size="sm"
            className="text-muted-foreground hover:text-foreground hover:bg-muted/50"
          >
            <LogOut className="h-4 w-4 mr-2" />
            {!isCollapsed && "Logout"}
          </Button>
        </div>
      </div>
    </aside>
  );
}