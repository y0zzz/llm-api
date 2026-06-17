# Step 1: Use an official, lightweight Python base image
FROM python:3.11-slim

# Step 2: Set system environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Step 3: Set the working directory inside the container
WORKDIR /app

# Step 4: Install system dependencies needed for python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Step 5: Copy and install Python dependencies
# Staging dependencies separately leverages Docker's cache layer for faster builds
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Copy the application code into the container
COPY main.py .
COPY database.py .

# Step 7: Create a non-privileged user for security
# Running containers as 'root' is a major DevOps security risk
RUN useradd -u 8888 appuser && chown -R appuser /app
USER appuser

# Step 8: Expose the application port
EXPOSE 8080

# Step 9: Define the command to run the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]