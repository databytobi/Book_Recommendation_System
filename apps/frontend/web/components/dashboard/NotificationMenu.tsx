// apps/frontend/web/components/layout/NotificationMenu.tsx

"use client";

import { useState, useMemo } from "react";
import { Bell, Check, Sparkles, BookOpen, Heart } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface Notification {
  id: string;
  type: "recommendation" | "book" | "follow" | "system";
  title: string;
  description: string;
  timestamp: Date;
  read: boolean;
  icon?: React.ReactNode;
}

interface NotificationMenuProps {
  className?: string;
  onNotificationClick?: (notification: Notification) => void;
}

const mockNotifications: Notification[] = [
  {
    id: "1",
    type: "recommendation",
    title: "New recommendation for you",
    description: "We found 5 books you might love",
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
    read: false,
    icon: <Sparkles className="h-4 w-4 text-amber-500" />,
  },
  {
    id: "2",
    type: "book",
    title: "The Great Gatsby is trending",
    description: "3 of your friends are reading this",
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
    read: false,
    icon: <BookOpen className="h-4 w-4 text-blue-500" />,
  },
  {
    id: "3",
    type: "follow",
    title: "Jane Doe followed you",
    description: "Started following your activity",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2),
    read: true,
    icon: <Heart className="h-4 w-4 text-emerald-500" />,
  },
];

export function NotificationMenu({
  onNotificationClick,
}: NotificationMenuProps) {
  const [notifications, setNotifications] = useState<Notification[]>(mockNotifications);
  const [isOpen, setIsOpen] = useState(false);

  // FIX: Use useMemo instead of useEffect for unreadCount
  const unreadCount = useMemo(() => {
    return notifications.filter(n => !n.read).length;
  }, [notifications]);

  const handleMarkAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
  };

  const handleMarkAllRead = () => {
    setNotifications(prev =>
      prev.map(n => ({ ...n, read: true }))
    );
  };

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.read) {
      handleMarkAsRead(notification.id);
    }
    onNotificationClick?.(notification);
    setIsOpen(false);
  };

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger className="relative flex h-9 w-9 items-center justify-center rounded-md hover:bg-muted/60 transition-all duration-200">
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-500 px-1.5 text-[10px] font-medium text-white ring-2 ring-background">
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end" className="w-[380px] max-h-[500px] p-0">
        {/* Base UI requires GroupLabel to live inside a Menu.Group; without
            this wrapper opening the dropdown threw
            "MenuGroupContext is missing" and crashed the whole page. */}
        <DropdownMenuGroup>
        <div className="flex items-center justify-between border-b border-border/40 px-4 py-3">
          <DropdownMenuLabel className="text-sm font-semibold px-0">
            Notifications
          </DropdownMenuLabel>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs text-muted-foreground hover:text-foreground"
              onClick={handleMarkAllRead}
            >
              <Check className="h-3.5 w-3.5 mr-1" />
              Mark all read
            </Button>
          )}
        </div>

        {notifications.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted/50">
              <Bell className="h-6 w-6 text-muted-foreground/50" />
            </div>
            <p className="mt-4 text-sm font-medium text-foreground">All caught up!</p>
            <p className="text-xs text-muted-foreground">No new notifications</p>
          </div>
        ) : (
          <ScrollArea className="max-h-[400px]">
            <div className="divide-y divide-border/40">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={cn(
                    "group relative cursor-pointer transition-colors hover:bg-muted/30 px-4 py-3",
                    !notification.read && "bg-primary/5"
                  )}
                  onClick={() => handleNotificationClick(notification)}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted/50">
                      {notification.icon || <Bell className="h-4 w-4 text-muted-foreground" />}
                    </div>
                    <div className="flex-1 min-w-0 space-y-1">
                      <p className={cn(
                        "text-sm",
                        !notification.read ? "font-medium text-foreground" : "text-muted-foreground"
                      )}>
                        {notification.title}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {notification.description}
                      </p>
                      <p className="text-[10px] text-muted-foreground/70">
                        {formatDistanceToNow(notification.timestamp, { addSuffix: true })}
                      </p>
                    </div>
                    {!notification.read && (
                      <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-blue-500" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}