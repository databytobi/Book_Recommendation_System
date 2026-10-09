"use client";

import { useState } from "react";
import { Check, SlidersHorizontal } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type ReadingGoal =
  | "light"
  | "moderate"
  | "avid"
  | "intense";

export type Language =
  | "en"
  | "es"
  | "fr"
  | "de"
  | "it"
  | "pt"
  | "nl"
  | "ru"
  | "ja"
  | "zh"
  | "ar"
  | "hi";

export type Theme =
  | "dark"
  | "light"
  | "system";

export interface PreferenceValues {
  reading_goal: ReadingGoal;
  preferred_language: Language;
  recommendation_count: number;
  theme: Theme;
}

interface PreferencesStepProps {
  initialValues?: Partial<PreferenceValues>;
  loading?: boolean;
  onContinue: (values: PreferenceValues) => void;
  className?: string;
}

const readingGoals: {
  id: ReadingGoal;
  label: string;
  description: string;
}[] = [
  {
    id: "light",
    label: "Light Reader",
    description: "1–5 books per year",
  },
  {
    id: "moderate",
    label: "Moderate Reader",
    description: "6–12 books per year",
  },
  {
    id: "avid",
    label: "Avid Reader",
    description: "13–24 books per year",
  },
  {
    id: "intense",
    label: "Book Lover",
    description: "25+ books per year",
  },
];

const languages: {
  id: Language;
  label: string;
}[] = [
  { id: "en", label: "English" },

];

const recommendationCounts = [10, 20, 30, 50];

const themes: {
  id: Theme;
  label: string;
  description: string;
}[] = [
  {
    id: "dark",
    label: "Dark",
    description: "Easy on the eyes",
  },
  {
    id: "light",
    label: "Light",
    description: "Clean and bright",
  },
  {
    id: "system",
    label: "System",
    description: "Follow your device",
  },
];

export function PreferencesStep({
  initialValues,
  loading = false,
  onContinue,
  className,
}: PreferencesStepProps) {
  const [values, setValues] = useState<PreferenceValues>({
    reading_goal:
      initialValues?.reading_goal ?? "moderate",

    preferred_language:
      initialValues?.preferred_language ?? "en",

    recommendation_count:
      initialValues?.recommendation_count ?? 20,

    theme:
      initialValues?.theme ?? "dark",
  });

  function updateValue<K extends keyof PreferenceValues>(
    key: K,
    value: PreferenceValues[K]
  ) {
    setValues((previous) => ({
      ...previous,
      [key]: value,
    }));
  }

  function handleContinue() {
    onContinue(values);
  }

  if (loading) {
    return (
      <div className="flex h-80 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div
      className={cn(
        "mx-auto w-full max-w-4xl space-y-10",
        className
      )}
    >
      {/* Header */}
      <div className="text-center">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
          <SlidersHorizontal className="h-7 w-7 text-primary" />
        </div>

        <h2 className="text-3xl font-bold">
          Customize Your Experience
        </h2>

        <p className="mt-3 text-muted-foreground">
          Tell us how you like to read so we can personalize
          your recommendations.
        </p>
      </div>

      {/* Reading Goal */}
      <section className="space-y-4">
        <div>
          <h3 className="text-xl font-semibold">
            How much do you read?
          </h3>

          <p className="text-sm text-muted-foreground">
            Choose the reading goal that best describes you.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {readingGoals.map((goal) => {
            const active =
              values.reading_goal === goal.id;

            return (
              <button
                key={goal.id}
                type="button"
                onClick={() =>
                  updateValue("reading_goal", goal.id)
                }
                className={cn(
                  "rounded-2xl border p-5 text-left transition-all",
                  active
                    ? "border-primary bg-primary text-primary-foreground shadow-lg"
                    : "bg-card hover:border-primary/40 hover:shadow-md"
                )}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-semibold">
                      {goal.label}
                    </h4>

                    <p
                      className={cn(
                        "mt-1 text-sm",
                        active
                          ? "text-primary-foreground/80"
                          : "text-muted-foreground"
                      )}
                    >
                      {goal.description}
                    </p>
                  </div>

                  {active && (
                    <Check className="h-5 w-5" />
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </section>

      {/* Language */}
      <section className="space-y-4">
        <div>
          <h3 className="text-xl font-semibold">
            Preferred language
          </h3>

          <p className="text-sm text-muted-foreground">
            Choose the language you'd like to use for
            recommendations.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
          {languages.map((language) => {
            const active =
              values.preferred_language === language.id;

            return (
              <button
                key={language.id}
                type="button"
                onClick={() =>
                  updateValue(
                    "preferred_language",
                    language.id
                  )
                }
                className={cn(
                  "rounded-xl border px-4 py-3 text-sm font-medium transition-all",
                  active
                    ? "border-primary bg-primary text-primary-foreground"
                    : "bg-card hover:border-primary/40"
                )}
              >
                {language.label}
              </button>
            );
          })}
        </div>
      </section>

      {/* Recommendation Count */}
      <section className="space-y-4">
        <div>
          <h3 className="text-xl font-semibold">
            How many recommendations?
          </h3>

          <p className="text-sm text-muted-foreground">
            Choose how many books you'd like to see at a time.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {recommendationCounts.map((count) => {
            const active =
              values.recommendation_count === count;

            return (
              <button
                key={count}
                type="button"
                onClick={() =>
                  updateValue(
                    "recommendation_count",
                    count
                  )
                }
                className={cn(
                  "rounded-xl border p-4 font-semibold transition-all",
                  active
                    ? "border-primary bg-primary text-primary-foreground"
                    : "bg-card hover:border-primary/40"
                )}
              >
                {count} books
              </button>
            );
          })}
        </div>
      </section>

      {/* Theme */}
      <section className="space-y-4">
        <div>
          <h3 className="text-xl font-semibold">
            Choose your theme
          </h3>

          <p className="text-sm text-muted-foreground">
            Select how you'd like the app to look.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          {themes.map((theme) => {
            const active = values.theme === theme.id;

            return (
              <button
                key={theme.id}
                type="button"
                onClick={() =>
                  updateValue("theme", theme.id)
                }
                className={cn(
                  "rounded-2xl border p-5 text-left transition-all",
                  active
                    ? "border-primary bg-primary text-primary-foreground shadow-lg"
                    : "bg-card hover:border-primary/40 hover:shadow-md"
                )}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-semibold">
                      {theme.label}
                    </h4>

                    <p
                      className={cn(
                        "mt-1 text-sm",
                        active
                          ? "text-primary-foreground/80"
                          : "text-muted-foreground"
                      )}
                    >
                      {theme.description}
                    </p>
                  </div>

                  {active && (
                    <Check className="h-5 w-5" />
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </section>

      {/* Continue */}
      <div className="flex justify-end border-t pt-6">
        <Button
          size="lg"
          onClick={handleContinue}
        >
          Continue
        </Button>
      </div>
    </div>
  );
}

export type { PreferencesStepProps };