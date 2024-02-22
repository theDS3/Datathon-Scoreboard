FROM python:3.12-slim as base

# Builder Process
FROM base as builder

WORKDIR /app/

# Creates virtual Python environment called venv
RUN python -m venv /opt/venv

# Added virtual environment to PATH
ENV PATH="/opt/venv/bin:$PATH"

# Copy the requirements file to the working directory
COPY requirements.txt /app/

# Install the Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt


# Runtime Process
FROM base as runtime

# Pulls virtual environemnt from builder process
COPY --from=builder /opt/venv /opt/venv

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Added virtual environment to PATH
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY src/main.py src/shared.py /app/src/

EXPOSE 8000

# Run the FastAPI application using uvicorn server
CMD uvicorn src.main:app --host 0.0.0.0 --port 8000
