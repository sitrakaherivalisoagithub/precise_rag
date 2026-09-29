# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables to prevent Python from writing .pyc files and to buffer output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code into the container
COPY . .

# Expose the port that the application will run on
EXPOSE 8000

# Command to run the application
# The application will listen on the port defined by the PORT environment variable,
# defaulting to 8000 if it's not set. This is required for Cloud Run.
CMD uvicorn main:api --host 0.0.0.0 --port ${PORT:-8000}
