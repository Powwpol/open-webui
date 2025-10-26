# syntax=docker/dockerfile:1

ARG NODE_VERSION=22.13.1
FROM node:${NODE_VERSION}-slim AS builder
WORKDIR /app

# Install dependencies (use npm ci for deterministic builds)
COPY --link package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Copy application source code
COPY --link . .

# Build the TypeScript/SvelteKit app
RUN --mount=type=cache,target=/root/.npm \
    npm run build

# Remove dev dependencies and install only production dependencies
RUN --mount=type=cache,target=/root/.npm \
    rm -rf node_modules && npm ci --production

# Production image
FROM node:${NODE_VERSION}-slim AS final
WORKDIR /app

# Create a non-root user for security
RUN useradd -m webuiuser
USER webuiuser

# Copy built app and production dependencies from builder
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

# Set environment variables
ENV NODE_ENV=production
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Expose port (default SvelteKit port is 3000, but can be overridden)
EXPOSE 3000

# Start the app (use SvelteKit preview for production)
CMD ["npm", "run", "preview"]
