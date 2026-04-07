FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential cmake git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir fastapi uvicorn pydantic

ENV PYTHONPATH="/app:/app/server"

CMD ["python3", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]