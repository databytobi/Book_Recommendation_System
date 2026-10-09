"use client";

import { useEffect, useState } from "react";
import { AuthGuard } from "@/features/auth/guard";
import { settingsService, UserSettings } from "@/lib/services/settings.service";

export default function SettingsPage() {
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await settingsService.getSettings();
        setSettings(data);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  if (loading) {
    return (
      <div className="py-20 text-center">
        Loading settings...
      </div>
    );
  }

  if (!settings) {
    return (
      <div className="py-20 text-center">
        Failed to load settings.
      </div>
    );
  }

  return (
    <AuthGuard>
      <div className="mx-auto max-w-3xl space-y-8">
        <div>
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground mt-2">
            Manage your reading preferences.
          </p>
        </div>

        <div className="rounded-xl border p-6 space-y-5">

          <div>
            <label className="text-sm font-medium">
              Reading Goal
            </label>

            <select
              value={settings.reading_goal}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  reading_goal: e.target.value,
                })
              }
              className="mt-2 w-full rounded-md border px-3 py-2"
            >
              <option value="light">Light</option>
              <option value="moderate">Moderate</option>
              <option value="intensive">Intensive</option>
            </select>
          </div>

          <div>
            <label className="text-sm font-medium">
              Reading Style
            </label>

            <select
              value={settings.reading_style}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  reading_style: e.target.value,
                })
              }
              className="mt-2 w-full rounded-md border px-3 py-2"
            >
              <option value="quick">Quick</option>
              <option value="balanced">Balanced</option>
              <option value="deep">Deep</option>
              <option value="explorer">Explorer</option>
            </select>
          </div>

          <div>
            <label className="text-sm font-medium">
              Language
            </label>

            <select
              value={settings.preferred_language}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  preferred_language: e.target.value,
                })
              }
              className="mt-2 w-full rounded-md border px-3 py-2"
            >
              <option value="en">English</option>
            </select>
          </div>

          <div>
            <label className="text-sm font-medium">
              Theme
            </label>

            <select
              value={settings.theme}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  theme: e.target.value,
                })
              }
              className="mt-2 w-full rounded-md border px-3 py-2"
            >
              <option value="dark">Dark</option>
              <option value="light">Light</option>
            </select>
          </div>

          <button
            onClick={async () => {
              await settingsService.updateSettings(settings);
              alert("Settings updated successfully!");
            }}
            className="w-full rounded-lg bg-primary py-3 text-primary-foreground"
          >
            Save Changes
          </button>

        </div>
      </div>
    </AuthGuard>
  );
}