FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN crawl4ai-setup

COPY . .

EXPOSE 8003

CMD ["uvicorn", "src.server:app", "--host","0.0.0.0","--port","8003"]