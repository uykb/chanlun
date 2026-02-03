# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Combine installation and cleanup of build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install TA-Lib C library
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Install uv for faster package installation
RUN pip install --no-cache-dir uv

COPY requirements.txt .
RUN uv pip install --no-cache-dir --system -r requirements.txt

# Stage 2: Final image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies including playwright browsers' system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    # Added for playwright (optional but needed if using screenshot alert)
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Selectively copy core directories instead of 'COPY . .'
COPY src/ /app/src/
COPY web/ /app/web/

# Set environment variables
ENV PYTHONPATH="/app/src"
ENV DATA_PATH="/app/data"
ENV WEB_HOST="0.0.0.0"

# Create data directory
RUN mkdir -p /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:9900/ || exit 1

EXPOSE 9900

# Default entrypoint for the web chart app
CMD ["python", "web/chanlun_chart/app.py", "nobrowser"]
