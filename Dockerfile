# ============================
# Stage 1: Builder (optional caching)
# ============================
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================
# Stage 2: Runtime
# ============================
FROM python:3.11-slim

ENV TZ=UTC
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Setup cron job
COPY cron/mycron /etc/cron.d/mycron
RUN chmod 0644 /etc/cron.d/mycron && crontab /etc/cron.d/mycron

# Create volume mount points
RUN mkdir -p /data /cron && chmod 755 /data /cron

EXPOSE 8080

# Start cron and server
CMD cron && uvicorn main:app --host 0.0.0.0 --port 8080
