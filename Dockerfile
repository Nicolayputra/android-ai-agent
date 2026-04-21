# NOIR SOVEREIGN v14.0 COMMANDER — VPS Docker Core
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies directly to avoid requirement mismatches
RUN pip install --no-cache-dir \
    requests \
    fastapi \
    uvicorn \
    python-dotenv \
    pyTelegramBotAPI \
    numpy \
    pandas \
    Pillow \
    opencv-python-headless \
    scikit-image \
    playwright \
    youtube-transcript-api \
    beautifulsoup4 \
    docker

# Copy source code
COPY . .

# Default command (overridden by docker-compose)
CMD ["python", "noir-vps/brain.py"]
