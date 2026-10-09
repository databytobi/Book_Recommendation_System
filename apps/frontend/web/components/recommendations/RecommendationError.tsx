// apps/frontend/web/components/recommendations/RecommendationError.tsx

"use client";

import { useState } from "react";
import type { LucideIcon } from "lucide-react";
import {
  AlertCircle,
  RefreshCw,
  WifiOff,
  Server,
  Zap,
  Clock,
  HelpCircle,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

// ======================================================
// TYPES
// ======================================================

interface RecommendationErrorProps {
  title?: string;
  description?: string;

  className?: string;

  onRetry?: () => Promise<void> | void;

  retryLabel?: string;

  variant?: "default" | "compact" | "minimal";

  errorType?:
    | "general"
    | "network"
    | "server"
    | "timeout"
    | "rate-limit";

  errorCode?: string;

  showDetails?: boolean;
}

interface ErrorConfig {
  icon: LucideIcon;
  color: string;
  bgColor: string;
  borderColor: string;
  defaultDescription: string;
  tip: string;
}

// ======================================================
// CONFIG
// ======================================================

const ERROR_CONFIG: Record<
  NonNullable<RecommendationErrorProps["errorType"]>,
  ErrorConfig
> = {
  general: {
    icon: AlertCircle,
    color: "text-destructive",
    bgColor: "bg-destructive/10",
    borderColor: "border-destructive/20",
    defaultDescription:
      "Something unexpected happened while loading recommendations.",
    tip: "Try refreshing the page.",
  },

  network: {
    icon: WifiOff,
    color: "text-amber-500",
    bgColor: "bg-amber-500/10",
    borderColor: "border-amber-500/20",
    defaultDescription:
      "We couldn't reach the recommendation service.",
    tip: "Check your internet connection.",
  },

  server: {
    icon: Server,
    color: "text-red-500",
    bgColor: "bg-red-500/10",
    borderColor: "border-red-500/20",
    defaultDescription:
      "The recommendation server is temporarily unavailable.",
    tip: "Please try again shortly.",
  },

  timeout: {
    icon: Clock,
    color: "text-orange-500",
    bgColor: "bg-orange-500/10",
    borderColor: "border-orange-500/20",
    defaultDescription:
      "The request took too long to complete.",
    tip: "Please retry in a moment.",
  },

  "rate-limit": {
    icon: Zap,
    color: "text-violet-500",
    bgColor: "bg-violet-500/10",
    borderColor: "border-violet-500/20",
    defaultDescription:
      "Too many requests were sent.",
    tip: "Wait a few seconds before retrying.",
  },
};

const BADGE_TEXT = {
  general: "Application Error",
  network: "Network Error",
  server: "Server Error",
  timeout: "Request Timeout",
  "rate-limit": "Rate Limited",
};

const HELP_TEXT = {
  general:
    "Something unexpected happened. Retrying usually fixes the problem.",

  network:
    "Check your internet connection and try again.",

  server:
    "Our servers are temporarily unavailable. Please try again shortly.",

  timeout:
    "The request timed out before finishing.",

  "rate-limit":
    "You've made too many requests in a short period.",
};

// ======================================================
// COMPONENT
// ======================================================

export function RecommendationError({
  title = "Couldn't load recommendations",

  description,

  className,

  onRetry,

  retryLabel = "Try Again",

  variant = "default",

  errorType = "general",

  errorCode,

  showDetails = false,
}: RecommendationErrorProps) {
  const [isRetrying, setIsRetrying] = useState(false);

  const [isHovered, setIsHovered] = useState(false);

  const config = ERROR_CONFIG[errorType];

  const Icon = config.icon;

  const errorDescription =
    description ?? config.defaultDescription;

  const handleRetry = async () => {
    if (!onRetry) return;

    setIsRetrying(true);

    try {
      await onRetry?.();
    } catch (error) {
      console.error(error);
    } finally {
      setIsRetrying(false);
    }
  };

  // ======================================================
  // COMPACT
  // ======================================================

  if (variant === "compact") {
    return (
      <div
        role="alert"
        aria-live="assertive"
        className={cn(
          "flex items-center gap-4 rounded-xl border p-4",
          config.borderColor,
          config.bgColor,
          className
        )}
      >
        <div className={cn("rounded-full p-2", config.bgColor)}>
          <Icon className={cn("h-5 w-5", config.color)} />
        </div>

        <div className="min-w-0 flex-1">
          <h4 className="text-sm font-semibold">
            {title}
          </h4>

          <p className="truncate text-sm text-muted-foreground">
            {errorDescription}
          </p>
        </div>

        {onRetry && (
          <Button
            size="sm"
            variant="outline"
            onClick={handleRetry}
            disabled={isRetrying}
            aria-busy={isRetrying}
          >
            {isRetrying ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              retryLabel
            )}
          </Button>
        )}
      </div>
    );
  }

  // ======================================================
  // MINIMAL
  // ======================================================

  if (variant === "minimal") {
    return (
      <div
        role="alert"
        aria-live="assertive"
        className={cn(
          "flex flex-col items-center justify-center py-10 text-center",
          className
        )}
      >
        <div className="mb-4 rounded-full bg-muted/40 p-4">
          <Icon className={cn("h-7 w-7", config.color)} />
        </div>

        <h4 className="text-lg font-semibold">
          {title}
        </h4>

        <p className="mt-2 max-w-sm text-sm text-muted-foreground">
          {errorDescription}
        </p>

        {onRetry && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRetry}
            disabled={isRetrying}
            aria-busy={isRetrying}
            className="mt-4 gap-2"
          >
            <RefreshCw
              className={cn(
                "h-4 w-4",
                isRetrying && "animate-spin"
              )}
            />

            {retryLabel}
          </Button>
        )}
      </div>
    );
  }

  // ======================================================
  // DEFAULT
  // ======================================================

  return (    <div
      role="alert"
      aria-live="assertive"
      className={cn(
        "relative overflow-hidden rounded-2xl border px-8 py-16 text-center transition-all duration-300",
        config.borderColor,
        config.bgColor,
        className
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Decorative Background */}
      <div className="absolute -top-24 -right-24 h-64 w-64 rounded-full bg-primary/5 blur-3xl" />
      <div className="absolute -bottom-24 -left-24 h-64 w-64 rounded-full bg-destructive/5 blur-3xl" />

      <div className="relative z-10 mx-auto max-w-xl">

        {/* Icon */}
        <div className="mb-6 inline-flex">
          <div
            className={cn(
              "rounded-full p-5 transition-all duration-300",
              config.bgColor,
              isHovered ? "scale-110" : "scale-100"
            )}
          >
            <Icon className={cn("h-9 w-9", config.color)} />
          </div>
        </div>

        {/* Badges */}
        <div className="mb-5 flex flex-wrap items-center justify-center gap-2">

          <Badge variant="destructive">
            {BADGE_TEXT[errorType]}
          </Badge>

          {errorCode && (
            <Badge variant="outline">
              {errorCode}
            </Badge>
          )}

        </div>

        {/* Title */}
        <h2 className="text-2xl font-bold tracking-tight">
          {title}
        </h2>

        {/* Description */}
        <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-muted-foreground">
          {errorDescription}
        </p>

        {/* Developer Details */}
        {showDetails && (
          <div className="mx-auto mt-6 rounded-xl border bg-background/60 p-4 text-left font-mono text-xs">

            <div className="space-y-2">

              <div className="flex justify-between">
                <span className="text-muted-foreground">
                  Error Type
                </span>

                <span className="font-semibold">
                  {errorType}
                </span>
              </div>

              {errorCode && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">
                    Error Code
                  </span>

                  <span className="font-semibold">
                    {errorCode}
                  </span>
                </div>
              )}

              <div className="flex justify-between">
                <span className="text-muted-foreground">
                  Timestamp
                </span>

                <span className="font-semibold">
                  {new Date().toLocaleString()}
                </span>
              </div>

            </div>

          </div>
        )}

        {/* Actions */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">

          {onRetry && (
            <Button
              onClick={handleRetry}
              disabled={isRetrying}
              className="min-w-[140px] gap-2"
              aria-busy={isRetrying}
            >
              <RefreshCw
                className={cn(
                  "h-4 w-4 transition-transform duration-300",
                  isRetrying && "animate-spin",
                  !isRetrying &&
                    isHovered &&
                    "rotate-180"
                )}
              />

              {isRetrying
                ? "Retrying..."
                : retryLabel}
            </Button>
          )}

          <Button
            variant="outline"
            size="icon"
            aria-label="Help"
          >
            <HelpCircle className="h-4 w-4" />
          </Button>

        </div>

        {/* Help Text */}
        <div className="mt-8 rounded-xl bg-background/60 px-5 py-4">

          <p className="text-sm font-medium">
            Troubleshooting
          </p>

          <p className="mt-1 text-sm text-muted-foreground">
            {HELP_TEXT[errorType]}
          </p>

        </div>

        {/* Tip */}
        <p className="mt-6 text-xs text-muted-foreground">
          {config.tip}
        </p>

      </div>
    </div>
  );
}