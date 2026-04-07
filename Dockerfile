# Use a standard Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# 1. Install essential system tools
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy your local files into the container
COPY . .

# 3. CRITICAL: Force-install the openenv library and server requirements
# We install openenv-core specifically to fix that "ModuleNotFoundError"
RUN pip install --no-cache-dir fastapi uvicorn pydantic openenv-core

# 4. Install the rest of your local project dependencies
RUN pip install --no-cache-dir .

# 5. Set the Python path so the 'server' folder is easy to find
ENV PYTHONPATH="${PYTHONPATH}:/app"

# 6. Start the server on Hugging Face's required port (7860)
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]