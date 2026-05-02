FROM python:3.11-slim
WORKDIR /app

# Cài thêm gcc, g++ vì các thư viện Machine Learning (XGBoost) cần nó để build
RUN apt-get update && apt-get install -y libpq-dev gcc g++

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000