# =========================
# STAGE 1: BUILD FRONTEND
# =========================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build


# =========================
# STAGE 2: BACKEND + SERVE
# =========================
FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# =========================
# COPY BACKEND
# =========================
COPY backend ./backend

# =========================
# COPY FRONTEND BUILD
# =========================
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/package.json ./frontend/package.json

# =========================
# INSTALL PYTHON DEPS
# =========================
RUN pip install --no-cache-dir -r backend/requirements.txt

# =========================
# INSTALL FRONTEND RUNTIME
# =========================
WORKDIR /app/frontend
RUN npm install --production

# =========================
# BACK TO ROOT
# =========================
WORKDIR /app

# =========================
# ENV
# =========================
ENV PORT=8080

# =========================
# CREATE REQUIRED FOLDERS
# =========================
RUN mkdir -p backend/uploads backend/vectors backend/logs

# =========================
# START BOTH SERVICES
# =========================
CMD sh -c "uvicorn backend.app.main:app --host 0.0.0.0 --port 8080 & cd frontend && npm start"