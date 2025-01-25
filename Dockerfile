# First stage: Build stage
FROM python:3.11-slim AS builder

# Set environment variables for the build stage
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies for Python build
# Using a single RUN command to reduce layers and optimize build time
# Adding no-install-recommends to avoid unnecessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libatlas-base-dev \
    liblapack-dev \
    libblas-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# Combining pip install commands to reduce layers
# Using --no-cache-dir to avoid storing unnecessary files
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Second stage: Final runtime stage
FROM python:3.11-slim AS runtime

# Set environment variables for the runtime stage
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy installed packages from the builder stage
COPY --from=builder /usr/local /usr/local

# Copy the project code into the container
COPY . /app/

