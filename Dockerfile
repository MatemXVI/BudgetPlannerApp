# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system deps (if needed for building some wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY .env .env


EXPOSE 8000

# Default envs (can be overridden by docker run / compose)
ENV SERVER_BASE_URL="http://localhost:8000" \
    DATABASE_URL="sqlite:////data/budget_planner.db"

# Create runtime dir for SQLite (mounted as volume in compose)
RUN mkdir -p /data

# Start the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
