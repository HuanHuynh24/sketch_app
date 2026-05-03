#!/bin/bash

# Kiểm tra xem người dùng có nhập tên service chưa
if [ -z "$1" ]; then
  echo "❌ Lỗi: Bạn chưa nhập tên service!"
  echo "💡 Cách dùng: ./make_service.sh ten_service"
  exit 1
fi

SERVICE_NAME=$1
SERVICE_PATH="services/$SERVICE_NAME"

echo "🚀 Đang khởi tạo service mới: $SERVICE_NAME..."

# 1. Copy toàn bộ từ bản mẫu (đã có sẵn Clean Architecture)
cp -r services/_template_service $SERVICE_PATH
cd $SERVICE_PATH

# 2. Tạo môi trường ảo và cài thư viện
echo "📦 Đang cài đặt môi trường ảo (venv) và thư viện..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

# 3. Chạy Migration đầu tiên để tự động tạo Database cho Service này
echo "🗄️ Đang cấu hình Database bằng Alembic..."
alembic revision --autogenerate -m "init_$SERVICE_NAME" > /dev/null 2>&1
alembic upgrade head > /dev/null 2>&1

echo "✅ HOÀN TẤT! Đã tạo xong $SERVICE_NAME và chạy sẵn Database."
echo "👉 Mã nguồn của bạn nằm tại: backend/$SERVICE_PATH"