#!/bin/bash

if [ -z "$1" ]; then
  echo "❌ Lỗi: Bạn chưa nhập tên service!"
  echo "💡 Cách dùng: ./make_service.sh ten_service"
  exit 1
fi

SERVICE_NAME=$1
SERVICE_PATH="services/$SERVICE_NAME"

if [ -d "$SERVICE_PATH" ]; then
  echo "❌ Service đã tồn tại: $SERVICE_PATH"
  exit 1
fi

echo "🚀 Đang khởi tạo service mới: $SERVICE_NAME..."

cp -r services/_template_service "$SERVICE_PATH"

find "$SERVICE_PATH" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find "$SERVICE_PATH" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
find "$SERVICE_PATH" -type d -name "venv" -exec rm -rf {} + 2>/dev/null

cat > "$SERVICE_PATH/.env.example" <<EOF
PROJECT_NAME=$SERVICE_NAME
API_PREFIX=/api/$SERVICE_NAME
DB_SCHEMA=$SERVICE_NAME
DATABASE_URL=postgresql://postgres:secret@postgres_db:5432/sketch_db
EOF

echo "✅ Đã tạo service: $SERVICE_NAME"
echo "👉 Path: backend/$SERVICE_PATH"
echo ""
echo "Bước tiếp theo:"
echo "1. Thêm service vào docker-compose.yml"
echo "2. Tạo model trong $SERVICE_PATH/app/models"
echo "3. Import model trong $SERVICE_PATH/alembic/env.py"
echo "4. Build service:"
echo "   docker compose up -d --build $SERVICE_NAME"
echo "5. Tạo migration:"
echo "   docker exec -it ms_$SERVICE_NAME alembic revision --autogenerate -m \"init_$SERVICE_NAME\""
echo "6. Apply migration:"
echo "   docker exec -it ms_$SERVICE_NAME alembic upgrade head"