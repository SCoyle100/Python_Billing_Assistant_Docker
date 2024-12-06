# Use the official Python image as a base
FROM python:3.10-slim

# Set a working directory in the container
WORKDIR /app

# Copy requirements and the application code to the working directory
COPY requirements.txt requirements.txt
COPY . .

# Install system dependencies for Python and Flask
RUN apt-get update && apt-get install -y \
    gcc \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Expose the port the app runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Start the application
CMD ["flask", "run"]
