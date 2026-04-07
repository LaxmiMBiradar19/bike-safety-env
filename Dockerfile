FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy all project files
COPY . .

# 1. Update pip
RUN pip install --upgrade pip

# 2. Force install openenv-core AND its dependencies
# We also install 'openenv' just in case the naming convention differs
RUN pip install --no-cache-dir fastapi uvicorn pydantic openenv-core openenv

# 3. Explicitly install the current directory
RUN pip install -e .

# 4. CRITICAL: Add the current directory to PYTHONPATH 
# This helps Python find your 'server' folder and 'models.py'
ENV PYTHONPATH="/app:${PYTHONPATH}"

# 5. Run uvicorn using the module path
CMD ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]