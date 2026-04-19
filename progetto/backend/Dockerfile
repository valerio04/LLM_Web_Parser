FROM python:3.10-slim

WORKDIR /app

COPY requirements.tx
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install -U crawl4ai
RUN crawl4ai-setup

COPY src/ ./src

EXPOSE 8003

CMD ["uvicorn", "src.server:app", "--host","0.0.0.0","--port","8003"]