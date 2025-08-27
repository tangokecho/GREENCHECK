FROM node:20-slim

WORKDIR /workspace/apps/web

# Install deps with caching
COPY apps/web/package.json apps/web/package-lock.json* ./
RUN npm ci || npm install

# Copy source
COPY apps/web ./

ENV PORT=3000 \
    NODE_ENV=development

EXPOSE 3000

# In dev, "npm run dev" is fine; in prod, switch to "npm run build && npm run start"
CMD ["npm", "run", "dev"]
