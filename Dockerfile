# Use the official Python base image
FROM python:3.12-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY * /app

# Install the Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8000

# Run the FastAPI application using uvicorn server
CMD uvicorn main:app --host 0.0.0.0 --port 8000
