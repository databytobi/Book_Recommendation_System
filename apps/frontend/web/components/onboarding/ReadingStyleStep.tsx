"use client";

import { useEffect, useState } from "react";
import {
  CheckCircle2,
  Loader2,
  Clock3,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type ReadingStyle =
  | "quick"
  | "balanced"
  | "deep"
  | "explorer";

export interface ReadingStyleOption {
  id: ReadingStyle;
  title: string;
  description: string;
}

interface ReadingStyleStepProps {
  styles: ReadingStyleOption[];
  loading?: boolean;
  error?: string | null;
  initialSelection?: ReadingStyle | null;
  onContinue: (style: ReadingStyle) => void;
  onRetry?: () => void;
  className?: string;
}

export function ReadingStyleStep({
  styles,
  loading = false,
  error = null,
  initialSelection = null,
  onContinue,
  onRetry,
  className,
}: ReadingStyleStepProps) {
  const [selected, setSelected] =
    useState<ReadingStyle | null>(initialSelection);

  useEffect(() => {
    queueMicrotask(() => {
      setSelected(initialSelection);
    });
  }, [initialSelection]);

  if (loading) {
    return (
      <div className="flex h-80 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-destructive/30 bg-destructive/5 p-8 text-center">
        <h3 className="font-semibold">
          Unable to load reading styles
        </h3>

        <p className="mt-2 text-sm text-muted-foreground">
          {error}
        </p>

        {onRetry && (
          <Button
            className="mt-5"
            onClick={onRetry}
          >
            Try Again
          </Button>
        )}
      </div>
    );
  }

  return (
    <div
      className={cn(
        "mx-auto w-full max-w-3xl space-y-8",
        className
      )}
    >
      <div className="text-center">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
          <Clock3 className="h-7 w-7 text-primary" />
        </div>

        <h2 className="text-3xl font-bold">
          What&apos;s Your Reading Style?
        </h2>

        <p className="mt-3 text-muted-foreground">
          Choose the option that best describes how you usually read.
        </p>
      </div>

      <div className="space-y-4">
        {styles.map((style) => {
          const active = selected === style.id;

          return (
            <button
              key={style.id}
              type="button"
              onClick={() => setSelected(style.id)}
              className={cn(
                "w-full rounded-2xl border p-6 text-left transition-all duration-200",
                active
                  ? "border-primary bg-primary text-primary-foreground shadow-lg"
                  : "bg-card hover:border-primary/40 hover:shadow-md"
              )}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="text-lg font-semibold">
                    {style.title}
                  </h3>

                  <p
                    className={cn(
                      "mt-2 text-sm",
                      active
                        ? "text-primary-foreground/80"
                        : "text-muted-foreground"
                    )}
                  >
                    {style.description}
                  </p>
                </div>

                {active && (
                  <CheckCircle2 className="h-6 w-6 shrink-0" />
                )}
              </div>
            </button>
          );
        })}
      </div>

      <div className="flex justify-end border-t pt-6">
        <Button
          size="lg"
          disabled={selected === null}
          onClick={() => {
            if (selected !== null) {
              onContinue(selected);
            }
          }}
        >
          Continue
        </Button>
      </div>
    </div>
  );
}

export type {
  ReadingStyleStepProps,
};