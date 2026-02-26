# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies for Rasterio and PyProj
RUN apt-get update && apt-get install -y \
	libexpat1 \
	libgdal-dev \
	g++ \
	&& rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Start the application
CMD ["gunicorn", "-b", "0.0.0.0:8080", "main:createApp()"]
