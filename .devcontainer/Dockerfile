# Use an official Python runtime as a parent image
FROM python:3.12.0-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app source code into the container at /app
# This includes all files in your build context (the directory containing the Dockerfile), 
# except those excluded by .dockerignore
COPY . /app/