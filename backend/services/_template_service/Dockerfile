FROM python:3.11-slim

WORKDIR /app

# Đặt biến môi trường để Python không viết file .pyc và in log trực tiếp
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

# Chỉ cài thư viện Python, không cần cài thêm gói hệ thống nào cả cho bản gốc
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Lệnh khởi chạy mặc định cho mọi service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]