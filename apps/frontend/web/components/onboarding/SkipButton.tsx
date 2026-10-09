"use client";

import { ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface SkipButtonProps {
  onSkip?: () => void;
  disabled?: boolean;
  className?: string;
}

export function SkipButton({
  onSkip,
  disabled = false,
  className,
}: SkipButtonProps) {
  return (
    <Button
      type="button"
      variant="ghost"
      onClick={onSkip}
      disabled={disabled}
      className={cn(
        "gap-2 text-muted-foreground hover:text-foreground",
        className
      )}
    >
      Skip for now
      <ChevronRight className="h-4 w-4" />
    </Button>
  );
}