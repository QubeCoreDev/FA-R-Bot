# ---- Stage 1: Build frontend ----
FROM node:20-slim AS frontend-build

ARG VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_localhost_dev

WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm ci --ignore-scripts
COPY frontend/ ./
ENV VITE_CHATKIT_API_DOMAIN_KEY=$VITE_CHATKIT_API_DOMAIN_KEY
RUN npm run build


# ---- Stage 2: Python backend + serve frontend ----
FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY backend/pyproject.toml backend/
RUN cd backend && uv venv /app/.venv && \
    UV_PROJECT_ENVIRONMENT=/app/.venv uv sync --no-dev

COPY backend/ backend/
COPY data/ data/
COPY --from=frontend-build /build/frontend/dist frontend/dist

ENV PATH="/app/.venv/bin:$PATH"
ENV FACR_DOCS_DIR=/app/data

EXPOSE 8002

CMD python -m uvicorn app.main:app \
    --app-dir backend \
    --host 0.0.0.0 \
    --port "${PORT:-8002}"
