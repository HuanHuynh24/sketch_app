FROM python:3.11-slim

WORKDIR /app

# Cài đặt các thư viện cần thiết cho hệ điều hành để build psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000