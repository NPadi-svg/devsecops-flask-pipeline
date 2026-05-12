# Use slim image to reduce attack surface — fewer packages = fewer CVEs
FROM python:3.11-slim

# Don't run as root — security best practice
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /home/appuser/app

# Copy and install dependencies first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Switch to non-root user
USER appuser

EXPOSE 5000

# Use init_db before starting so DB is ready
CMD ["python", "app/main.py"]