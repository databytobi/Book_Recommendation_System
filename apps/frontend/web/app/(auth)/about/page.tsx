// apps/frontend/web/app/(auth)/about/page.tsx

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "About",
  description:
    "How the Hybrid Book Recommendation System generates personalized recommendations.",
};

export default function AboutPage() {
  return (
    <article className="prose prose-slate max-w-none dark:prose-invert">
      <h1 className="text-2xl font-semibold tracking-tight">
        About this project
      </h1>

      <p className="mt-4 text-sm text-muted-foreground">
        A hybrid recommendation engine for book discovery — built to surface
        titles you would not have found by searching, rather than the same
        bestsellers everyone else sees.
      </p>

      <h2 className="mt-8 text-lg font-semibold">How recommendations work</h2>
      <p className="mt-3 text-sm">
        Three independent signals are combined into a single ranking:
      </p>
      <ul className="mt-3 list-disc space-y-2 pl-6 text-sm">
        <li>
          <strong>Collaborative filtering</strong> — what readers with similar
          taste enjoyed, learned with implicit-feedback matrix factorisation.
        </li>
        <li>
          <strong>Semantic similarity</strong> — books whose descriptions sit
          close to ones you already liked, found with a vector index over
          sentence embeddings.
        </li>
        <li>
          <strong>Popularity</strong> — a recency- and diversity-adjusted
          quality signal, which also serves new users with no history yet.
        </li>
      </ul>

      <h2 className="mt-8 text-lg font-semibold">Technology</h2>
      <p className="mt-3 text-sm">
        FastAPI and PostgreSQL on the backend, Next.js on the frontend, with
        Redis for caching, FAISS for vector search, and Prometheus for
        observability.
      </p>

      <h2 className="mt-8 text-lg font-semibold">Built with</h2>
      <p className="mt-3 text-sm">
        Open catalogue data from the Book-Crossing and Goodreads datasets.
      </p>
    </article>
  );
}