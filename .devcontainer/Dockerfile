# Use an official Python runtime as a parent image
FROM python:3.10.8-slim

# Set the working directory in the container
WORKDIR /app

# Install required Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app source code
COPY . /app