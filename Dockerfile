# Use slim image to reduce attack surface — fewer packages = fewer CVEs
FROM python:3.11-slim

# Don't run as root — security best practice
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /home/appuser/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

USER appuser

EXPOSE 5000

CMD ["python", "app/main.py"]