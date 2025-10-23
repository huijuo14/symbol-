FROM python:3.9-alpine

# Install Chromium and dependencies on Alpine
RUN apk add --no-cache \
    chromium \
    chromium-chromedriver \
    bash \
    gcc \
    musl-dev \
    libffi-dev

# Copy application
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "symbol_solver.py"]