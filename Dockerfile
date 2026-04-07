FROM python:3.10-slim

WORKDIR /app

# Install system essentials
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# 1. Force install everything into a specific location
RUN pip install --no-cache-dir fastapi uvicorn pydantic openenv-core

# 2. Copy your files
COPY . .

# 3. ABSOLUTE PATH INJECTION: This is the fix.
# This tells Python exactly where the 'openenv_core' library was installed 
# and where your 'server' folder is.
ENV PYTHONPATH="/app:/app/server:/usr/local/lib/python3.10/site-packages"

# 4. Use the specific python runner
CMD ["python3", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]