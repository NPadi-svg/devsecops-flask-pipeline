# Use slim image to reduce attack surface — fewer packages = fewer CVEs
FROM python:3.11-slim

# Don't run as root — security best practice
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /home/appuser/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Create a writable directory for the SQLite database
RUN mkdir -p /home/appuser/data && chown appuser:appuser /home/appuser/data

USER appuser

EXPOSE 5000

ENV DB_PATH=/home/appuser/data/todos.db

CMD ["python", "app/main.py"]