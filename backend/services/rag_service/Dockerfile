FROM python:3.11-slim
WORKDIR /app

# ChromaDB cũng cần build C++ core
RUN apt-get update && apt-get install -y libpq-dev gcc g++

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000