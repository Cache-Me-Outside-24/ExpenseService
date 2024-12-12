FROM python:3.11-slim

WORKDIR /app

# Copy service account key
COPY service-account-key.json /app/service-account-key.json

# Set the environment variable for Google Application Credentials
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
