# Use a standard Python image
FROM python:3.10-slim

# Set the working directory to the root of the project
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
RUN pip install --no-cache-dir fastapi uvicorn pydantic openenv-core

# Set the PYTHONPATH so Python can find your modules in the server folder
ENV PYTHONPATH="/app:/app/server"

# Move into the server folder to run the app
WORKDIR /app/server

# Start uvicorn on the port Hugging Face requires (7860)
CMD ["python3", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]