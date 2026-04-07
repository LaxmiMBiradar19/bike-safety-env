FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy everything first
COPY . .

# 1. Force install the specific version of openenv-core
# We also include 'openenv' as a separate install to catch naming variations
RUN pip install --no-cache-dir fastapi uvicorn pydantic openenv-core openenv

# 2. Install your local project in editable mode
RUN pip install -e .

# 3. SET THE PATH: This is the most likely culprit
# This ensures Python looks in the site-packages AND your app folder
ENV PYTHONPATH="/app:/usr/local/lib/python3.10/site-packages"

# 4. Use the python module runner to start uvicorn
# This is more reliable than calling 'uvicorn' directly in Docker
CMD ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]