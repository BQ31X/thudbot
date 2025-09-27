# apps/frontend/Dockerfile

# ---------- Build stage ----------
    FROM node:20 AS builder

    WORKDIR /app
    
    # Copy only package manifests first (better build caching)
    COPY package*.json ./
    
    # Install dependencies
    RUN npm ci
    
    # Copy the rest of the source
    COPY . .
    
    # Build the Next.js app for production
    RUN npm run build
    
# ---------- Runtime stage ----------
FROM node:20-alpine AS runner

WORKDIR /app

# Create a non-root user for security
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Copy only the necessary output from the builder
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./next.config.js

# Change ownership to non-root user
RUN chown -R nextjs:nodejs /app
USER nextjs

# Set environment to production
ENV NODE_ENV=production
EXPOSE 3000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Start Next.js in production mode
CMD ["npm", "start"]
    