# Build context is frontend/. Local dev image: Vite dev server with HMR.
# The SPA reaches the backend through the Vite proxy (BACKEND_ORIGIN).
FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
