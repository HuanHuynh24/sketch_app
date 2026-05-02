# api_gateway/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy và cài đặt thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code
COPY . .

EXPOSE 8000