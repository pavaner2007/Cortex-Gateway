# ─────────────────────────────────────────────────────────────────────────────
# Cortex Gateway – Frontend Dockerfile
# Stage 1: Build React app with Vite
# Stage 2: Serve with Nginx
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (better layer caching)
COPY package*.json ./
RUN npm ci --frozen-lockfile

# Copy source and build
COPY . .
RUN npm run build

# ── Stage 2: Production Nginx ─────────────────────────────────────────────────
FROM nginx:1.27-alpine AS production

# Copy compiled assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx config (SPA routing + API proxy)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf.bak 2>/dev/null || true

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD wget -q -O /dev/null http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
