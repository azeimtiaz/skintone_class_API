# Use Ubuntu base image
FROM ubuntu:20.04

# Update package lists and install necessary packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory in the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt /app/

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements2.txt

# Copy the application code
COPY . /app/

# Expose port
EXPOSE 8080

# Command to run the application
CMD ["python3", "app.py"]
