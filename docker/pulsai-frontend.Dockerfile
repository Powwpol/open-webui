# Pulsai Frontend - Production Dockerfile
# Multi-stage build: Node build + Nginx serve
# Build from LOCAL files

ARG NODE_VERSION=20

# ============================================
# Stage 1: Builder
# ============================================
FROM node:${NODE_VERSION}-alpine AS builder

WORKDIR /build

# Install git for prepare-pyodide script
RUN apk add --no-cache git

# Copy package files
COPY package.json package-lock.json ./
COPY scripts ./scripts

# Install dependencies
ENV NODE_OPTIONS="--max-old-space-size=8192"
RUN npm config set fetch-retries 5 && \
    npm config set fetch-retry-maxtimeout 600000 && \
    mkdir -p static/pyodide && \
    npm config set legacy-peer-deps true && \
    npm ci --prefer-offline && \
    npm cache clean --force

# Copy ALL source code from LOCAL
COPY src ./src
COPY static ./static
COPY svelte.config.js ./
COPY vite.config.ts ./
COPY tsconfig.json ./
COPY tailwind.config.js ./
COPY postcss.config.js ./
COPY i18next-parser.config.ts ./
COPY .prettierrc ./
COPY .eslintrc.cjs ./

# Build application (includes Pyodide fetch)
RUN npm run build

# ============================================
# Stage 2: Nginx Runtime
# ============================================
FROM nginx:alpine

LABEL maintainer="Pulsai Team"
LABEL description="Pulsai Frontend"

# Copy custom Nginx configuration
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Copy built app from builder
COPY --from=builder /build/build /usr/share/nginx/html

# Copy static assets
COPY --from=builder /build/static /usr/share/nginx/html/static

# Create health check endpoint
RUN echo 'OK' > /usr/share/nginx/html/health

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/health || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]

