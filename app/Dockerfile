FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

ENV PYTHONPATH=/app
# Copy application code
COPY . /app

# Create necessary directories
# RUN mkdir -p data/output/figs data/output/jsons data/output/ds

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["fastapi", "run", "--workers", "4", "web/main.py"]