FROM python:3.10-slim

WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy your files into the container
COPY . .

# Install OpenEnv and dependencies
RUN pip install --no-cache-dir openenv-core pydantic uvicorn fastapi

# The command to launch your environment as a server
CMD ["python", "-m", "openenv.server", "--env", "environment:BikeSafetyEnv"]