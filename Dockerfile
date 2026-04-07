FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system tools needed for building packages
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy all project files into the container
COPY . .

# Force install the core requirements and the library
# This ensures openenv_core is available for your app.py imports
RUN pip install --no-cache-dir fastapi uvicorn pydantic openenv-core

# Install the current directory as an editable package
RUN pip install -e .

# CRITICAL: Tell Python to look inside the /app folder for your server module
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Run uvicorn on the port Hugging Face requires (7860)
# We point to 'server.app:app' because app.py is inside the 'server' folder
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]