import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Required for Docker standalone builds
  output: "standalone",

  // Turbopack configuration for Next.js 16+
  turbopack: {
    root: __dirname,
  },

  // Transpile specific packages if needed
  transpilePackages: [],

  // Enable React strict mode
  reactStrictMode: false,

  // Image configuration
  images: {
    remotePatterns: [
      // The catalog's legacy host. It now answers HTTP 403 for every image,
      // so covers served from here never render; kept only so old cached
      // records do not hard-fail the optimizer.
      {
        protocol: "http",
        hostname: "images.amazon.com",
        pathname: "/images/P/**",
      },
      {
        protocol: "https",
        hostname: "images.amazon.com",
        pathname: "/images/P/**",
      },
      // Modern TLS host that serves the identical cover objects. The API
      // rewrites legacy URLs to this host (see app/core/images.py), so it
      // MUST be allowlisted or next/image rejects every book cover.
      {
        protocol: "https",
        hostname: "images-na.ssl-images-amazon.com",
        pathname: "/images/P/**",
      },
      // Fallback source, used if the catalog is ever re-pointed at
      // Open Library covers.
      {
        protocol: "https",
        hostname: "covers.openlibrary.org",
        pathname: "/b/isbn/**",
      },
    ],
    qualities: [75, 85],
  },

  experimental: {},

  webpack: (config) => {
    return config;
  },
};

export default nextConfig;