# syntax=docker/dockerfile:1
# ============================================================
# Next.js frontend — production image
#
# Build context: apps/frontend/web
#   docker build -f infrastructure/docker/frontend/Dockerfile apps/frontend/web
# ============================================================

# ------------------------------------------------------------
# 1. Dependencies
# ------------------------------------------------------------
FROM node:22-alpine AS deps
WORKDIR /app

COPY package.json package-lock.json ./
# `npm ci` requires the lockfile to be in sync with package.json.
RUN npm ci

# ------------------------------------------------------------
# 2. Build
# ------------------------------------------------------------
FROM node:22-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
# NEXT_PUBLIC_* values are inlined into the client bundle at build time,
# so the API URL must be supplied here — not only at runtime.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

RUN npm run build

# ------------------------------------------------------------
# 3. Production runtime
# ------------------------------------------------------------
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create a non-root user and group in a single layer.
RUN addgroup --system --gid 1001 nodejs \
 && adduser --system --uid 1001 --ingroup nodejs nextjs

# Public assets are served statically by the Next.js server.
COPY --from=builder /app/public ./public

# `output: "standalone"` emits a self-contained server bundle.
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Container-level healthcheck so orchestrators and compose can gate on it.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD node -e "require('http').get('http://127.0.0.1:3000/',r=>process.exit(r.statusCode<500?0:1)).on('error',()=>process.exit(1))"

CMD ["node", "server.js"]