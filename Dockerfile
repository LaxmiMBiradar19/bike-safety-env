FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential cmake git && rm -rf /var/lib/apt/lists/*

COPY . .

# Force install the exact library name
RUN pip install --no-cache-dir fastapi uvicorn pydantic openenv-core

# This tells Python to look in the /app/server folder for imports
ENV PYTHONPATH="/app/server"

# We run it directly from the folder where app.py lives
WORKDIR /app/server
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]