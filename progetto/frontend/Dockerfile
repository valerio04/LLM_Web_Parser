FROM python:3.10-slim

WORKDIR /app

COPY requirements.tx
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src

EXPOSE 8004

CMD ["python", "src/frontend.py"]