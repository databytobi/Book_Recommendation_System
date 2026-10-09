// apps/frontend/web/components/auth/AuthCard.tsx

import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface AuthCardProps {
  children: ReactNode;
  className?: string;
  title?: string;
  description?: string;
  showHeader?: boolean;
}

export function AuthCard({
  children,
  className,
  title,
  description,
  showHeader = true,
}: AuthCardProps) {
  return (
    <div
      className={cn(
        "w-full max-w-md rounded-2xl border border-border bg-card p-6 sm:p-8 shadow-sm",
        "transition-all duration-200 hover:shadow-md",
        className
      )}
    >
      {showHeader && (title || description) && (
        <div className="mb-6 space-y-1.5">
          {title && (
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              {title}
            </h2>
          )}
          {description && (
            <p className="text-sm text-muted-foreground">
              {description}
            </p>
          )}
        </div>
      )}

      {children}
    </div>
  );
}

// Alternative version with more features
export function AuthCardWithFooter({
  children,
  className,
  title,
  description,
  footer,
  showHeader = true,
}: AuthCardProps & {
  footer?: ReactNode;
}) {
  return (
    <div
      className={cn(
        "w-full max-w-md rounded-2xl border border-border bg-card shadow-sm",
        "transition-all duration-200 hover:shadow-md",
        className
      )}
    >
      {/* Header */}
      {showHeader && (title || description) && (
        <div className="border-b border-border px-6 sm:px-8 py-4 sm:py-5">
          <div className="space-y-1">
            {title && (
              <h2 className="text-xl sm:text-2xl font-semibold tracking-tight text-foreground">
                {title}
              </h2>
            )}
            {description && (
              <p className="text-sm text-muted-foreground">
                {description}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Body */}
      <div className="px-6 sm:px-8 py-6 sm:py-8">
        {children}
      </div>

      {/* Footer */}
      {footer && (
        <div className="border-t border-border px-6 sm:px-8 py-4 sm:py-5">
          {footer}
        </div>
      )}
    </div>
  );
}

// Compact version for smaller screens
export function AuthCardCompact({
  children,
  className,
  title,
  description,
}: AuthCardProps) {
  return (
    <div
      className={cn(
        "w-full max-w-sm rounded-xl border border-border bg-card p-5 shadow-sm",
        "transition-all duration-200 hover:shadow-md",
        className
      )}
    >
      {title && (
        <h2 className="text-xl font-semibold tracking-tight text-foreground mb-1">
          {title}
        </h2>
      )}
      {description && (
        <p className="text-sm text-muted-foreground mb-4">
          {description}
        </p>
      )}
      {children}
    </div>
  );
}