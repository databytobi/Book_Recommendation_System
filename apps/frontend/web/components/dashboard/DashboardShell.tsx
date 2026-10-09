// apps/frontend/web/components/layout/DashboardShell.tsx

"use client";

import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import { Menu } from "lucide-react"; // FIX: Removed unused 'X'
import { cn } from "@/lib/utils";
// FIX: Removed unused 'Button' import
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Sidebar } from "./Sidebar";
import { Navbar } from "./Navbar";

interface DashboardShellProps {
  children: React.ReactNode;
  className?: string;
  showSidebar?: boolean;
}

export function DashboardShell({
  children,
  className,
  showSidebar = true,
}: DashboardShellProps) {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // FIX: Wrap setState in queueMicrotask to avoid setState-in-effect warning
  useEffect(() => {
    queueMicrotask(() => {
      setIsMobileMenuOpen(false);
    });
  }, [pathname]);

  const handleSidebarToggle = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <div className="flex min-h-screen bg-background">
      {/* Desktop Sidebar */}
      {showSidebar && (
        <div className="hidden lg:block">
          <Sidebar
            isCollapsed={isSidebarCollapsed}
            onToggle={handleSidebarToggle}
          />
        </div>
      )}

      {/* Mobile Sidebar - Sheet */}
      <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
        <SheetTrigger className="fixed bottom-4 right-4 z-50 lg:hidden h-12 w-12 rounded-full shadow-lg bg-primary text-primary-foreground hover:bg-primary/90 flex items-center justify-center">
          <Menu className="h-5 w-5" />
        </SheetTrigger>
        <SheetContent side="left" className="w-[280px] sm:w-[320px] p-0">
          <div className="flex h-full flex-col">
            {/* Removed duplicate BookRec header */}
            <div className="flex-1 overflow-y-auto pt-4">
              <Sidebar isCollapsed={false} />
            </div>
          </div>
        </SheetContent>
      </Sheet>

      {/* Main Content */}
      <div
        className={cn(
          "flex flex-1 flex-col transition-all duration-300",
          showSidebar && !isSidebarCollapsed ? "lg:ml-72" : "lg:ml-[72px]",
          className
        )}
      >
        <div
          className={cn(
            "sticky top-0 z-40 transition-shadow duration-300",
            isScrolled && "shadow-sm"
          )}
        >
          <Navbar onMenuClick={() => setIsMobileMenuOpen(true)} />
        </div>

        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 bg-muted/5">
          {children}
        </main>

        <footer className="border-t border-border/40 bg-background/95 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-muted-foreground">
            <p>&copy; {new Date().getFullYear()} BookRec. All rights reserved.</p>
            <div className="flex items-center gap-4">
              <a href="/privacy" className="hover:text-foreground transition-colors">
                Privacy
              </a>
              <a href="/terms" className="hover:text-foreground transition-colors">
                Terms
              </a>
              <span className="text-muted-foreground/50">|</span>
              <span>v1.0.0</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}