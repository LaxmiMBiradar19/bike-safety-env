FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential cmake git && rm -rf /var/lib/apt/lists/*

# 1. Install every possible variation of the library
RUN pip install --no-cache-dir fastapi uvicorn pydantic openenv-core openenv

# 2. DEBUG STEP: This will print all installed modules to your logs
RUN pip list

COPY . .

# 3. Set the path to include the root and the server folder
ENV PYTHONPATH="/app:/app/server"

# 4. Use a more robust startup command
CMD ["python3", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "debug"]