# Single-stage runtime for TrainLoop Evals UI
FROM node:20-slim
WORKDIR /app

# pass VERSION at build-time
ARG VERSION
RUN test -n "$VERSION" || (echo "ERROR: version argument is required" && false)

# Set environment variables
ENV NODE_ENV=production \
  NEXT_TELEMETRY_DISABLED=1 \
  PORT=3000 \
  VERSION=${VERSION}

# Add labels
LABEL org.opencontainers.image.version=$VERSION \
  org.opencontainers.image.title="TrainLoop Evals UI" \
  org.opencontainers.image.source="https://github.com/trainloop/evals"

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
  adduser  --system --uid 1001 nextjs

# Copy only runtime files (assumes app is built locally)
COPY package.json ./
COPY next.config.mjs ./
COPY .next/ ./.next/
COPY public/ ./public/
COPY node_modules/ ./node_modules/
# Handle .env.production file - will be handled differently in build.py

# Switch to non-root user for runtime
USER nextjs

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/ || exit 1

CMD ["npm", "run", "start"]
