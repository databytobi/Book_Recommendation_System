import type { Metadata } from "next";
// FIX: Removed unused Geist and Geist_Mono imports
import { AuthProvider } from "@/features/auth/provider";
import "./globals.css";

export const metadata: Metadata = {
  title: "Book Recommendation System",
  description: "Discover your next favorite book",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}