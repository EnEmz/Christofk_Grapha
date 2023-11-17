# Use an official Python runtime as a parent image
FROM python:3.12.0-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install needed packages for Christofk_Grapha
RUN pip Install --no-cache-dir -r requirements.txt