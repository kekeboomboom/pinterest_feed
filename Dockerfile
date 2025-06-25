FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99

# Set work directory
WORKDIR /app

# Install system dependencies including browser dependencies for Pinterest scraping
RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    git \
    firefox-esr \
    xvfb \
    xorg \
    xserver-xephyr \
    dbus-x11 \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create directories for database, logs and static files
RUN mkdir -p /app/db /app/logs /app/staticfiles

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Note: Static files will be collected during deployment

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "pinterest_feed.wsgi:application"]
