// apps/frontend/web/components/ui/password-input.tsx

"use client";

import { useState, forwardRef } from "react";
import { Eye, EyeOff } from "lucide-react";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface PasswordInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  /**
   * Whether to show the password toggle button
   * @default true
   */
  showToggle?: boolean;
  
  /**
   * Custom label for the input (for accessibility)
   */
  label?: string;
  
  /**
   * Error message to display
   */
  error?: string;
}

export const PasswordInput = forwardRef<HTMLInputElement, PasswordInputProps>(
  (
    { 
      className, 
      showToggle = true, 
      label, 
      error, 
      disabled,
      placeholder = "Enter password",
      onFocus,
      onBlur,
      ...props 
    },
    ref
  ) => {
    const [showPassword, setShowPassword] = useState(false);
    const [isFocused, setIsFocused] = useState(false);

    const togglePasswordVisibility = () => {
      setShowPassword((prev) => !prev);
    };

    const hasError = !!error;
    const inputId = props.id || "password-input";

    return (
      <div className="space-y-2 w-full">
        {/* Label */}
        {label && (
          <label
            htmlFor={inputId}
            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            {label}
          </label>
        )}

        <div className="relative">
          {/* Input */}
          <Input
            ref={ref}
            id={inputId}
            type={showPassword ? "text" : "password"}
            placeholder={placeholder}
            disabled={disabled}
            className={cn(
              "pr-10",
              hasError && "border-destructive focus-visible:ring-destructive",
              isFocused && "ring-2 ring-ring ring-offset-2",
              className
            )}
            onFocus={(event) => {
              setIsFocused(true);
              onFocus?.(event);
            }}
            onBlur={(event) => {
              setIsFocused(false);
              onBlur?.(event);
            }}
            aria-invalid={hasError}
            aria-describedby={hasError ? `${inputId}-error` : undefined}
            {...props}
          />
          {/* Toggle Button */}
          {showToggle && (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className={cn(
                "absolute right-1 top-1/2 -translate-y-1/2",
                "h-8 w-8 rounded-md",
                "text-muted-foreground hover:text-foreground",
                "transition-colors duration-200",
                "focus-visible:ring-2 focus-visible:ring-ring",
                disabled && "opacity-50 cursor-not-allowed"
              )}
              onClick={togglePasswordVisibility}
              disabled={disabled}
              aria-label={showPassword ? "Hide password" : "Show password"}
              tabIndex={0}
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </Button>
          )}
        </div>

        {/* Error Message */}
        {hasError && (
          <p
            id={`${inputId}-error`}
            className="text-sm font-medium text-destructive"
          >
            {error}
          </p>
        )}
      </div>
    );
  }
);

PasswordInput.displayName = "PasswordInput";

// ============================================================
// ALTERNATIVE: PasswordInput with strength indicator
// ============================================================

interface PasswordInputWithStrengthProps extends PasswordInputProps {
  onStrengthChange?: (strength: number) => void;
  showStrength?: boolean;
}

export function PasswordInputWithStrength({
  onStrengthChange,
  showStrength = true,
  ...props
}: PasswordInputWithStrengthProps) {
  const [strength, setStrength] = useState(0);

  const calculateStrength = (value: string): number => {
    let score = 0;
    
    if (value.length >= 8) score += 1;
    if (value.length >= 12) score += 1;
    if (/[a-z]/.test(value) && /[A-Z]/.test(value)) score += 1;
    if (/\d/.test(value)) score += 1;
    if (/[^a-zA-Z0-9]/.test(value)) score += 1;
    
    return Math.min(score, 5);
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = e.target.value;
    const newStrength = calculateStrength(value);
    setStrength(newStrength);
    onStrengthChange?.(newStrength);
    props.onChange?.(e);
  };

  const getStrengthColor = (score: number): string => {
    if (score <= 1) return "bg-destructive";
    if (score <= 2) return "bg-orange-500";
    if (score <= 3) return "bg-yellow-500";
    if (score <= 4) return "bg-blue-500";
    return "bg-emerald-500";
  };

  const getStrengthLabel = (score: number): string => {
    if (score <= 1) return "Weak";
    if (score <= 2) return "Fair";
    if (score <= 3) return "Good";
    if (score <= 4) return "Strong";
    return "Very Strong";
  };

  return (
    <div className="space-y-2 w-full">
      <PasswordInput
        {...props}
        onChange={handleChange}
      />

      {showStrength && String(props.value ?? "").length > 0 && (
        <div className="space-y-1">
          <div className="flex h-1.5 gap-1 overflow-hidden rounded-full">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className={cn(
                  "w-full h-full transition-all duration-300 rounded-full",
                  i < strength ? getStrengthColor(strength) : "bg-muted"
                )}
              />
            ))}
          </div>

          <div className="flex justify-between text-xs text-muted-foreground">
            <span>
              Strength:{" "}
              <span className="font-medium">
                {getStrengthLabel(strength)}
              </span>
            </span>

            <span>
              {String(props.value ?? "").length} characters
            </span>
          </div>
        </div>
      )}
    </div>
  );
}