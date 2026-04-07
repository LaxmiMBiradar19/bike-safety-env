FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy your files
COPY . .

# FORCE INSTALL the openenv library and other core needs
RUN pip install --no-cache-dir fastapi uvicorn openenv-core pydantic

# Also try to install from your local pyproject.toml if available
RUN pip install --no-cache-dir . 

# Use port 7860 for Hugging Face
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]