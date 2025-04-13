FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Create a non-root user
RUN addgroup --system app && \
    adduser --system --group app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder stage
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy project files
COPY . .

# Set environment variables from .env file if it exists
RUN if [ -f .env ]; then export $(cat .env | grep -v '^#' | xargs); fi

# Only run collectstatic if not in debug mode
RUN if [ "$DEBUG" != "True" ]; then python manage.py collectstatic --noinput; fi

# Create media and static directories with proper permissions
RUN mkdir -p /app/media /app/staticfiles
RUN chown -R app:app /app

# Switch to non-root user
USER app

EXPOSE 8000

# Use Gunicorn with optimized settings
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--keep-alive", "5", "--max-requests", "1000", "--max-requests-jitter", "50"]
