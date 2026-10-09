// apps/frontend/web/app/(auth)/privacy/page.tsx

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "How the Book Recommendation System handles your data.",
};

export default function PrivacyPage() {
  return (
    <article className="prose prose-slate max-w-none dark:prose-invert">
      <h1 className="text-2xl font-semibold tracking-tight">
        Privacy Policy
      </h1>

      <p className="mt-4 text-sm text-muted-foreground">
        This policy explains what data the Book Recommendation System collects,
        why it is collected, and the choices available to you.
      </p>

      <h2 className="mt-8 text-lg font-semibold">Data we collect</h2>
      <ul className="mt-3 list-disc space-y-2 pl-6 text-sm">
        <li>
          <strong>Account data</strong> — your email address, username, and a
          bcrypt hash of your password. Passwords are never stored in plain text.
        </li>
        <li>
          <strong>Reading activity</strong> — books you rate, favourite, follow,
          or mark as read, plus the interactions used to personalise results.
        </li>
        <li>
          <strong>Usage telemetry</strong> — which recommendations are shown and
          clicked, used to measure ranking quality.
        </li>
      </ul>

      <h2 className="mt-8 text-lg font-semibold">How your data is used</h2>
      <p className="mt-3 text-sm">
        Reading activity is used solely to generate recommendations and to
        evaluate how well they perform. We do not sell personal data, and we do
        not share it with third parties for advertising.
      </p>

      <h2 className="mt-8 text-lg font-semibold">Your choices</h2>
      <p className="mt-3 text-sm">
        You can request a copy of your data or ask for your account to be
        deleted at any time. Deleting your account removes your profile,
        favourites, and interaction history.
      </p>

      <h2 className="mt-8 text-lg font-semibold">Contact</h2>
      <p className="mt-3 text-sm">
        Questions about this policy can be sent to the project maintainers.
      </p>
    </article>
  );
}