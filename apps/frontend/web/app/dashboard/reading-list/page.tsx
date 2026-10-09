"use client";

import { AuthGuard } from "@/features/auth/guard";

export default function ReadingListPage() {
  return (
    <AuthGuard>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Reading List</h1>
          <p className="text-muted-foreground mt-2">
            Books you've saved to read later.
          </p>
        </div>

        <div className="rounded-xl border border-dashed p-12 text-center">
          <h3 className="text-lg font-semibold">No books yet</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Save books from Discover or Recommendations and they'll appear here.
          </p>
        </div>
      </div>
    </AuthGuard>
  );
}