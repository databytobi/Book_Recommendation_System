// apps/frontend/web/app/(auth)/terms/page.tsx

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service",
  description: "Terms governing use of the Book Recommendation System.",
};

export default function TermsPage() {
  return (
    <article className="prose prose-slate max-w-none dark:prose-invert">
      <h1 className="text-2xl font-semibold tracking-tight">
        Terms of Service
      </h1>

      <p className="mt-4 text-sm text-muted-foreground">
        By creating an account you agree to the terms below.
      </p>

      <h2 className="mt-8 text-lg font-semibold">Acceptable use</h2>
      <p className="mt-3 text-sm">
        Use the service for personal book discovery. Do not attempt to scrape
        the catalogue at scale, disrupt the service, or access accounts that are
        not yours.
      </p>

      <h2 className="mt-8 text-lg font-semibold">Your account</h2>
      <p className="mt-3 text-sm">
        You are responsible for keeping your credentials secure and for activity
        that occurs under your account. Notify the maintainers if you believe
        your account has been compromised.
      </p>

      <h2 className="mt-8 text-lg font-semibold">Recommendations</h2>
      <p className="mt-3 text-sm">
        Recommendations are generated automatically and are provided for
        guidance only. They may be inaccurate or incomplete, and they are not
        professional advice.
      </p>

      <h2 className="mt-8 text-lg font-semibold">Availability</h2>
      <p className="mt-3 text-sm">
        The service is provided on an as-is basis without warranty of
        uninterrupted availability.
      </p>
    </article>
  );
}