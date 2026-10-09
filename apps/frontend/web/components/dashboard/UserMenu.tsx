// apps/frontend/web/components/layout/UserMenu.tsx

"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  User,
  Settings,
  LogOut,
  BookOpen,
  Heart,
  Library,
  ChevronDown,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/features/auth/useAuth";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface UserMenuProps {
  className?: string;
  showName?: boolean;
}

export function UserMenu({
  className,
}: UserMenuProps) {
  const router = useRouter();
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

  const getInitials = () => {
    const name = user?.full_name || user?.username || "User";
    const parts = name.split(" ");
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  const displayName = user?.full_name || user?.username || "User";
  const displayEmail = user?.email || "";

  const handleLogout = async () => {
    try {
      await logout();
      router.push("/login");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      {/* DropdownMenuTrigger - Only show avatar, no name/email */}
      <DropdownMenuTrigger className={cn(
        "flex items-center gap-2 rounded-md px-2 py-1.5 hover:bg-muted/60 transition-all duration-200 data-[state=open]:bg-muted/60",
        className
      )}>
        <div className="flex items-center gap-2">
          <Avatar className="h-8 w-8 ring-2 ring-primary/10">
            <AvatarFallback className="bg-gradient-to-br from-indigo-600 to-violet-600 text-white text-xs font-medium">
              {getInitials()}
            </AvatarFallback>
          </Avatar>

          {/* Only show the chevron, no name/email */}
          <ChevronDown
            className={cn(
              "h-4 w-4 text-muted-foreground transition-transform duration-200",
              isOpen && "rotate-180"
            )}
          />
        </div>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end" className="w-72 p-1.5" sideOffset={8}>
        {/* User Header - Show name and email ONLY in the dropdown */}
        <div className="flex items-center gap-3 px-2 py-3 rounded-lg bg-muted/30">
          <Avatar className="h-12 w-12 ring-2 ring-primary/10">
            <AvatarFallback className="bg-gradient-to-br from-indigo-600 to-violet-600 text-white text-sm font-medium">
              {getInitials()}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold truncate">{displayName}</p>
            <p className="text-xs text-muted-foreground truncate">{displayEmail}</p>
          </div>
        </div>

        <DropdownMenuSeparator />

        <DropdownMenuGroup>
          <DropdownMenuItem className="p-0">
            <Link
              href="/dashboard/profile"
              className="flex w-full items-center gap-2 px-2 py-1.5 rounded-sm hover:bg-muted"
            >
              <User className="h-4 w-4" />
              <span>Profile</span>
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem className="p-0">
            <Link
              href="/dashboard/library"
              className="flex w-full items-center gap-2 px-2 py-1.5 rounded-sm hover:bg-muted"
            >
              <Library className="h-4 w-4" />
              <span>My Library</span>
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem className="p-0">
            <Link
              href="/dashboard/reading-list"
              className="flex w-full items-center gap-2 px-2 py-1.5 rounded-sm hover:bg-muted"
            >
              <BookOpen className="h-4 w-4" />
              <span>Reading List</span>
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem className="p-0">
            <Link
              href="/dashboard/favorites"
              className="flex w-full items-center gap-2 px-2 py-1.5 rounded-sm hover:bg-muted"
            >
              <Heart className="h-4 w-4" />
              <span>Favorites</span>
            </Link>
          </DropdownMenuItem>
        </DropdownMenuGroup>

        <DropdownMenuSeparator />

        <DropdownMenuGroup>
          <DropdownMenuItem className="p-0">
            <Link
              href="/dashboard/settings"
              className="flex w-full items-center gap-2 px-2 py-1.5 rounded-sm hover:bg-muted"
            >
              <Settings className="h-4 w-4" />
              <span>Settings</span>
            </Link>
          </DropdownMenuItem>
        </DropdownMenuGroup>

        <DropdownMenuSeparator />

        <DropdownMenuItem
          onClick={handleLogout}
          className="cursor-pointer text-red-500 focus:text-red-500 focus:bg-red-50 dark:focus:bg-red-950/20"
        >
          <LogOut className="mr-2 h-4 w-4" />
          <span>Logout</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}