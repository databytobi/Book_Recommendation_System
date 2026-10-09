"use client";

import { useEffect, useState } from "react";
import { Mail, Calendar, BookOpen, Heart, User } from "lucide-react";
import {
  profileService,
  type ProfileSummary,
} from "@/lib/services/profile.service";

export default function ProfilePage() {
  const [profile, setProfile] = useState<ProfileSummary | null>(null);

  useEffect(() => {
    profileService.getProfile().then(setProfile);
  }, []);

  if (!profile) {
    return (
      <div className="flex justify-center py-20">
        Loading profile...
      </div>
    );
  }

  const joinDate = profile.user.created_at
    ? new Date(profile.user.created_at).toLocaleDateString()
    : "Not available";

  return (
    <div className="space-y-8">
      <div className="rounded-2xl border bg-background p-8">
        <div className="flex items-center gap-6">
          <div className="flex h-24 w-24 items-center justify-center rounded-full bg-primary/10">
            <User className="h-12 w-12 text-primary" />
          </div>

          <div>
            <h1 className="text-3xl font-bold">
              {profile.user.full_name}
            </h1>

            <div className="mt-2 flex items-center gap-2 text-muted-foreground">
              <Mail className="h-4 w-4" />
              {profile.user.email}
            </div>

            <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4" />
              Joined {joinDate}
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-xl border p-6">
          <div className="flex items-center gap-3">
            <BookOpen className="h-6 w-6 text-primary" />
            <h3 className="font-semibold">Books Read</h3>
          </div>

          <p className="mt-4 text-4xl font-bold">
            {profile.booksRead}
          </p>
        </div>

        <div className="rounded-xl border p-6">
          <div className="flex items-center gap-3">
            <Heart className="h-6 w-6 text-red-500" />
            <h3 className="font-semibold">Favorite Books</h3>
          </div>

          <p className="mt-4 text-4xl font-bold">
            {profile.favorites}
          </p>
        </div>
      </div>
    </div>
  );
}