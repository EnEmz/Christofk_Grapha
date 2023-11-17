# Use an official Python runtime as a parent image
FROM python:3.12.0-slim

# Set the working directory in the container
WORKDIR /app

# Install required Python packages
# Here, COPY command assumes that requirements.txt is in the build context root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app source code
# This copies everything from the build context root to /app in the container
COPY . /app