FROM python:3.9-slim

# Install Chromium and create swap
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    && fallocate -l 1G /swapfile \
    && chmod 600 /swapfile \
    && mkswap /swapfile \
    && swapon /swapfile \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy application
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "symbol_solver.py"]