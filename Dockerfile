FROM python:3.9-slim

# Install Firefox and geckodriver
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    && wget -q https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz \
    && tar -xzf geckodriver-*.tar.gz -C /usr/local/bin/ \
    && chmod +x /usr/local/bin/geckodriver \
    && rm geckodriver-*.tar.gz \
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