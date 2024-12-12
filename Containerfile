FROM python:3.11-slim

WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

ENV PYTHONUNBUFFERED=1

# Use the PORT environment variable provided by Cloud Run
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
